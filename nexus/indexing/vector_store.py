"""
Unified Component Vector Store.
Integrates AST metadata, dense embeddings, HNSW ANN graph indexing,
and APIRec MMR re-ranking with domain filtering and persistence.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from pydantic import BaseModel
import numpy as np

from nexus.parser.models import ComponentMetadata
from .embedder import DenseEmbedder
from .hnsw_index import HNSWIndex
from .mmr_reranker import APIRecMMRReranker


class SearchResult(BaseModel):
    component_id: str
    name: str
    domain: str
    description: str
    capabilities: List[str]
    score: float
    file_path: str
    props_count: int


class ComponentVectorStore:
    """
    Component-aware Vector Store for Nexus Tool Registry.
    """

    def __init__(
        self,
        embedder: Optional[DenseEmbedder] = None,
        hnsw_index: Optional[HNSWIndex] = None,
        mmr_reranker: Optional[APIRecMMRReranker] = None,
    ):
        self.embedder = embedder or DenseEmbedder()
        self.hnsw_index = hnsw_index or HNSWIndex(dimension=self.embedder.dimension)
        self.mmr_reranker = mmr_reranker or APIRecMMRReranker(lambda_param=0.6)

        self.metadata_store: Dict[str, ComponentMetadata] = {}
        self.embeddings_store: Dict[str, np.ndarray] = {}

    def add_component(self, meta: ComponentMetadata, embedding: Optional[np.ndarray] = None):
        """
        Add or update component in the store and HNSW index.
        """
        cid = meta.component_id
        if embedding is None:
            embedding = self.embedder.embed_query(meta.composite_representation)

        self.metadata_store[cid] = meta
        self.embeddings_store[cid] = embedding
        self.hnsw_index.add_item(cid, embedding)

    def delete_component(self, component_id: str):
        if component_id in self.metadata_store:
            del self.metadata_store[component_id]
        if component_id in self.embeddings_store:
            del self.embeddings_store[component_id]
        self.hnsw_index.delete_item(component_id)

    def search(
        self,
        query: str,
        top_k: int = 5,
        use_mmr: bool = True,
        lambda_param: float = 0.75,
        domain_filter: Optional[str] = None,
        candidate_pool_multiplier: int = 3,
    ) -> List[SearchResult]:
        """
        Execute component retrieval.
        1. Query embedding
        2. HNSW ANN search (retrieves pool of candidates)
        3. Domain filter (if specified)
        4. APIRec MMR diversity re-ranking over eligible candidates
        5. Return typed SearchResult objects with true cosine relevance scores
        """
        if not self.metadata_store:
            return []

        query_vec = self.embedder.embed_query(query)

        # Retrieve a candidate pool for re-ranking
        pool_size = min(len(self.metadata_store), max(top_k * candidate_pool_multiplier, 10))
        candidates_raw = self.hnsw_index.search_knn(query_vec, k=pool_size)

        # Apply domain filter if requested
        filtered_candidates = []
        for cid, sim in candidates_raw:
            meta = self.metadata_store.get(cid)
            if not meta:
                continue
            if domain_filter and meta.domain != domain_filter:
                continue
            filtered_candidates.append((cid, sim))

        if not filtered_candidates:
            return []

        # Filter out near-zero/irrelevant candidates to prevent MMR diversity penalty distortion
        top_sim = filtered_candidates[0][1] if filtered_candidates else 1.0
        min_sim_threshold = max(0.04, 0.20 * top_sim)
        eligible_candidates = [
            (cid, sim) for cid, sim in filtered_candidates if sim >= min_sim_threshold
        ]
        if not eligible_candidates and filtered_candidates:
            eligible_candidates = [filtered_candidates[0]]

        cand_ids = [cid for cid, _ in eligible_candidates]
        cand_scores = {cid: sim for cid, sim in eligible_candidates}

        if use_mmr and len(cand_ids) > 1:
            caps_map = {cid: self.metadata_store[cid].capabilities for cid in cand_ids}
            ranked = self.mmr_reranker.rerank(
                query_vector=query_vec,
                candidate_ids=cand_ids,
                candidate_vectors=self.embeddings_store,
                candidate_scores=cand_scores,
                top_k=top_k,
                capabilities_map=caps_map,
                lambda_override=lambda_param,
            )
        else:
            ranked = [(cid, cand_scores[cid]) for cid in cand_ids[:top_k]]

        results: List[SearchResult] = []
        for cid, _ in ranked:
            meta = self.metadata_store[cid]
            results.append(
                SearchResult(
                    component_id=meta.component_id,
                    name=meta.name,
                    domain=meta.domain,
                    description=meta.description,
                    capabilities=meta.capabilities,
                    score=float(cand_scores.get(cid, 0.0)),
                    file_path=meta.file_path,
                    props_count=len(meta.props),
                )
            )

        return results

    def save(self, directory: str | Path):
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Save metadata
        meta_dict = {cid: meta.to_dict() for cid, meta in self.metadata_store.items()}
        with open(dir_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2)

        # Save HNSW index
        self.hnsw_index.save(dir_path / "hnsw_index.json")

        # Save embeddings
        np.savez_compressed(
            dir_path / "embeddings.npz",
            **{cid: vec for cid, vec in self.embeddings_store.items()}
        )

    @classmethod
    def load(cls, directory: str | Path, embedder: Optional[DenseEmbedder] = None) -> "ComponentVectorStore":
        dir_path = Path(directory)
        embedder = embedder or DenseEmbedder()

        # Load metadata
        with open(dir_path / "metadata.json", "r", encoding="utf-8") as f:
            meta_dict = json.load(f)

        # Load HNSW
        hnsw_index = HNSWIndex.load(dir_path / "hnsw_index.json")

        # Load embeddings
        npz = np.load(dir_path / "embeddings.npz")
        embeddings_store = {k: npz[k] for k in npz.files}

        store = cls(embedder=embedder, hnsw_index=hnsw_index)
        store.embeddings_store = embeddings_store
        store.metadata_store = {
            cid: ComponentMetadata(**data) for cid, data in meta_dict.items()
        }
        return store
