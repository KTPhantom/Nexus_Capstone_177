"""
Unit tests for dense embedding module.
"""

import numpy as np
from nexus.indexing.embedder import DenseEmbedder


def test_embedder_dimension_and_norm():
    embedder = DenseEmbedder()
    assert embedder.dimension == 384

    texts = [
        "Focus timer for student studying intervals",
        "Point of sale cash ledger and UPI payment tracking",
    ]
    vectors = embedder.embed_texts(texts)

    assert vectors.shape == (2, 384)
    # Check L2 unit norm
    for vec in vectors:
        norm = np.linalg.norm(vec)
        assert abs(norm - 1.0) < 1e-4


def test_embed_query_similarity():
    embedder = DenseEmbedder()
    q = "academic study timer intervals"
    v_query = embedder.embed_query(q)

    v_timer = embedder.embed_query("Pomodoro focus timer with breaks and sessions")
    v_cash = embedder.embed_query("Cash drawer ledger and retail money balance")

    sim_timer = float(np.dot(v_query, v_timer))
    sim_cash = float(np.dot(v_query, v_cash))

    # Study timer should have much higher semantic similarity than cash ledger
    assert sim_timer > sim_cash
