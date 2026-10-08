"""
Unit tests for HNSW graph index.
"""

import tempfile
from pathlib import Path
import numpy as np
from nexus.indexing.hnsw_index import HNSWIndex


def test_hnsw_construction_and_search():
    dim = 64
    rng = np.random.RandomState(42)
    idx = HNSWIndex(dimension=dim, M=8, ef_construction=32, ef_search=16)

    # Insert 20 random normalized vectors
    items = {}
    for i in range(20):
        vec = rng.randn(dim).astype(np.float32)
        vec /= np.linalg.norm(vec)
        cid = f"item_{i}"
        items[cid] = vec
        idx.add_item(cid, vec)

    # Query with item_0
    q = items["item_0"]
    results = idx.search_knn(q, k=3)

    assert len(results) == 3
    # item_0 should be the top match
    assert results[0][0] == "item_0"
    assert abs(results[0][1] - 1.0) < 1e-4


def test_hnsw_deletion():
    dim = 32
    idx = HNSWIndex(dimension=dim, M=4)
    v1 = np.ones(dim, dtype=np.float32) / np.sqrt(dim)
    v2 = -np.ones(dim, dtype=np.float32) / np.sqrt(dim)

    idx.add_item("a", v1)
    idx.add_item("b", v2)

    assert "a" in idx.vectors
    idx.delete_item("a")
    assert "a" not in idx.vectors

    res = idx.search_knn(v1, k=2)
    assert len(res) == 1
    assert res[0][0] == "b"


def test_hnsw_serialization(tmp_path):
    dim = 16
    idx = HNSWIndex(dimension=dim, M=4)
    vec = np.ones(dim, dtype=np.float32) / np.sqrt(dim)
    idx.add_item("test_item", vec)

    save_file = tmp_path / "test_hnsw.json"
    idx.save(save_file)

    loaded = HNSWIndex.load(save_file)
    assert "test_item" in loaded.vectors
    res = loaded.search_knn(vec, k=1)
    assert res[0][0] == "test_item"


def test_hnsw_multi_level_enter_point_deletion():
    """
    Critical Regression Test: Deleting the HNSW enter point must reassign
    the enter point to a node strictly at max_level, ensuring upper-level
    graph routing is never disconnected.
    """
    dim = 16
    idx = HNSWIndex(dimension=dim, M=4, ef_construction=32, ef_search=16, seed=42)
    rng = np.random.RandomState(42)

    # Insert 50 items to ensure multi-layer hierarchy
    items = {}
    for i in range(50):
        vec = rng.randn(dim).astype(np.float32)
        vec /= np.linalg.norm(vec)
        cid = f"node_{i}"
        items[cid] = vec
        idx.add_item(cid, vec)

    assert idx.max_level >= 1
    assert idx.enter_point is not None
    assert idx.levels[idx.enter_point] == idx.max_level

    # Delete the enter point
    original_ep = idx.enter_point
    idx.delete_item(original_ep)

    assert original_ep not in idx.vectors
    assert idx.enter_point is not None
    assert idx.enter_point in idx.vectors
    # Enter point must be at max_level
    assert idx.levels[idx.enter_point] == idx.max_level

    # Search should still succeed and find the nearest neighbor among remaining nodes
    target_vec = items["node_5"] if original_ep != "node_5" else items["node_6"]
    expected_id = "node_5" if original_ep != "node_5" else "node_6"
    results = idx.search_knn(target_vec, k=3)
    assert len(results) == 3
    assert results[0][0] == expected_id
    assert abs(results[0][1] - 1.0) < 1e-4
