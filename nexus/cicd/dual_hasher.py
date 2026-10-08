import hashlib
import json
from typing import Literal

def compute_raw_sha256(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""

def compute_semantic_sha256(component_metadata) -> str:
    s = json.dumps(component_metadata, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def classify_change(manifest_entry, current_raw_sha, current_semantic_sha) -> Literal["unchanged", "cosmetic", "semantic", "new"]:
    if not manifest_entry:
        return "new"
    if manifest_entry.get("semantic_sha") != current_semantic_sha:
        return "semantic"
    if manifest_entry.get("raw_sha") != current_raw_sha:
        return "cosmetic"
    return "unchanged"
