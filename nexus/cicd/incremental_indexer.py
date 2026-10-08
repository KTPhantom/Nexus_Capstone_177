"""
Incremental and Idempotent Component Indexer.
Tracks component state via index_manifest.json with dual hashing:
- raw_code_sha256: Detects any file touch/edit
- semantic_sha256: Detects functional/semantic changes (ignores cosmetic Tailwind/CSS edits)
Ensures cost-effective, deterministic vector store synchronization.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from nexus.parser.ast_engine import TSXComponentParser
from nexus.indexing.embedder import DenseEmbedder
from nexus.indexing.vector_store import ComponentVectorStore


class IncrementalIndexer:
    def __init__(
        self,
        registry_dir: str | Path = "registry",
        index_dir: str | Path = "vector_index",
        embedder: Optional[DenseEmbedder] = None,
    ):
        self.registry_dir = Path(registry_dir)
        self.index_dir = Path(index_dir)
        self.manifest_path = self.index_dir / "index_manifest.json"

        self.parser = TSXComponentParser()
        self.embedder = embedder or DenseEmbedder()

        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()

        # Load or initialize vector store
        if (self.index_dir / "metadata.json").exists():
            self.store = ComponentVectorStore.load(self.index_dir, embedder=self.embedder)
        else:
            self.store = ComponentVectorStore(embedder=self.embedder)

    def _load_manifest(self) -> Dict[str, Any]:
        if self.manifest_path.exists():
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"components": {}, "last_run": None}

    def _save_manifest(self):
        self.manifest["last_run"] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2)

    def sync(self) -> Dict[str, List[str]]:
        """
        Execute incremental sync:
        - Detect new components
        - Detect modified components (differentiating semantic changes from cosmetic CSS changes)
        - Detect deleted components
        - Update vector store and HNSW index idempotently
        """
        current_files = list(self.registry_dir.glob("*/*.tsx"))
        found_paths = {str(f.resolve()): f for f in current_files}

        stats = {
            "added": [],
            "updated": [],
            "skipped_cosmetic": [],
            "unchanged": [],
            "deleted": [],
        }

        # Check existing and new files
        active_cids = set()

        for f_path, file_obj in found_paths.items():
            meta = self.parser.parse_file(file_obj)
            cid = meta.component_id
            active_cids.add(cid)

            record = self.manifest["components"].get(cid)

            if record is None:
                # Brand new component
                self.store.add_component(meta)
                self.manifest["components"][cid] = {
                    "file_path": meta.file_path,
                    "raw_code_sha256": meta.raw_code_sha256,
                    "semantic_sha256": meta.semantic_sha256,
                    "last_indexed_at": datetime.now(timezone.utc).isoformat(),
                }
                stats["added"].append(cid)
            else:
                # File exists in manifest, check hashes
                if record.get("raw_code_sha256") == meta.raw_code_sha256 and record.get("semantic_sha256") == meta.semantic_sha256:
                    stats["unchanged"].append(cid)
                elif record.get("semantic_sha256") == meta.semantic_sha256:
                    # Raw code changed (e.g. Tailwind CSS classes edited), but semantic AST unchanged!
                    stats["skipped_cosmetic"].append(cid)
                    # Update raw hash in manifest without expensive re-embedding
                    record["raw_code_sha256"] = meta.raw_code_sha256
                    record["last_verified_at"] = datetime.now(timezone.utc).isoformat()
                else:
                    # Functional semantic logic or chunking representation changed -> re-embed
                    self.store.add_component(meta)
                    record["raw_code_sha256"] = meta.raw_code_sha256
                    record["semantic_sha256"] = meta.semantic_sha256
                    record["last_indexed_at"] = datetime.now(timezone.utc).isoformat()
                    stats["updated"].append(cid)

        # Detect deleted files
        stored_cids = list(self.manifest["components"].keys())
        for cid in stored_cids:
            if cid not in active_cids:
                self.store.delete_component(cid)
                del self.manifest["components"][cid]
                stats["deleted"].append(cid)

        # Persist index and manifest
        self.store.save(self.index_dir)
        self._save_manifest()

        return stats
