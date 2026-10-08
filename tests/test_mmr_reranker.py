"""
Unit tests for APIRec MMR diversity re-ranker.
"""

import numpy as np
from nexus.indexing.mmr_reranker import APIRecMMRReranker


def test_mmr_diversity_penalty():
    reranker = APIRecMMRReranker(lambda_param=0.5)

    # Let query be along dimension 0
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    # Cand A: almost identical to query
    cand_a = np.array([0.99, 0.1, 0.0], dtype=np.float32)
    cand_a /= np.linalg.norm(cand_a)

    # Cand B: duplicate clone of Cand A
    cand_b = np.array([0.98, 0.12, 0.0], dtype=np.float32)
    cand_b /= np.linalg.norm(cand_b)

    # Cand C: different direction, but still relevant
    cand_c = np.array([0.75, 0.65, 0.0], dtype=np.float32)
    cand_c /= np.linalg.norm(cand_c)

    vectors = {"A": cand_a, "B": cand_b, "C": cand_c}
    scores = {"A": 0.99, "B": 0.98, "C": 0.75}

    # Pure greedy (lambda=1.0) ranks A, B, C
    greedy_ranks = reranker.rerank(
        query_vector=query,
        candidate_ids=["A", "B", "C"],
        candidate_vectors=vectors,
        candidate_scores=scores,
        top_k=3,
        lambda_override=1.0,
    )
    assert [cid for cid, _ in greedy_ranks] == ["A", "B", "C"]

    # MMR with lambda=0.3 penalizes the redundant twin B, selecting C ahead of B!
    mmr_ranks = reranker.rerank(
        query_vector=query,
        candidate_ids=["A", "B", "C"],
        candidate_vectors=vectors,
        candidate_scores=scores,
        top_k=3,
        lambda_override=0.3,
    )
    assert mmr_ranks[0][0] == "A"
    assert mmr_ranks[1][0] == "C"  # C was picked before duplicate B!
    assert mmr_ranks[2][0] == "B"


def test_mmr_orthogonal_irrelevant_candidate_protection():
    """
    Test that an orthogonal candidate with near-zero relevance (e.g. from the wrong domain)
    is not inappropriately ranked ahead of relevant candidates when using balanced lambda.
    """
    reranker = APIRecMMRReranker(lambda_param=0.75)
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    # Item A: High relevance (0.90)
    cand_a = np.array([0.90, 0.435, 0.0], dtype=np.float32)
    # Item B: Moderate relevance (0.50)
    cand_b = np.array([0.50, 0.866, 0.0], dtype=np.float32)
    # Item C: Irrelevant, orthogonal candidate (0.01)
    cand_c = np.array([0.01, 0.0, 0.999], dtype=np.float32)

    vectors = {"A": cand_a, "B": cand_b, "C": cand_c}
    scores = {"A": 0.90, "B": 0.50, "C": 0.01}

    ranked = reranker.rerank(
        query_vector=query,
        candidate_ids=["A", "B", "C"],
        candidate_vectors=vectors,
        candidate_scores=scores,
        top_k=3,
        lambda_override=0.75,
    )
    ranked_ids = [cid for cid, _ in ranked]
    assert ranked_ids[0] == "A"
    assert ranked_ids[1] == "B"  # B should beat irrelevant C
    assert ranked_ids[2] == "C"
