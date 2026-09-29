"""
Evaluation Metrics for Retrieval Benchmarking.
Implements Recall@K, MRR (Mean Reciprocal Rank), NDCG@K (Normalized Discounted Cumulative Gain),
and latency tracking (Manning et al., 2008; Elliott & Clark, 2024).
"""

import math
from typing import List, Dict
from pydantic import BaseModel


class BenchmarkMetrics(BaseModel):
    pipeline_name: str
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    mrr: float
    ndcg_at_5: float
    mean_latency_ms: float
    p95_latency_ms: float


def recall_at_k(retrieved_ids: List[str], ground_truth: Dict[str, int], k: int) -> float:
    """
    Computes Recall@K: fraction of relevant target components present in top-K retrieved.
    """
    relevant_targets = [cid for cid, rel in ground_truth.items() if rel > 0]
    if not relevant_targets:
        return 1.0

    top_k_retrieved = set(retrieved_ids[:k])
    hits = sum(1 for cid in relevant_targets if cid in top_k_retrieved)
    return hits / len(relevant_targets)


def reciprocal_rank(retrieved_ids: List[str], ground_truth: Dict[str, int]) -> float:
    """
    Computes reciprocal rank: 1 / (rank of first relevant component).
    Returns 0.0 if no relevant component is retrieved.
    """
    for rank, cid in enumerate(retrieved_ids, start=1):
        if ground_truth.get(cid, 0) > 0:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: List[str], ground_truth: Dict[str, int], k: int = 5) -> float:
    """
    Computes Normalized Discounted Cumulative Gain at rank K (NDCG@K) with exponential gain:
    DCG@K = sum_{i=1}^K (2^{rel_i} - 1) / log2(i + 1)
    """
    top_k = retrieved_ids[:k]
    dcg = 0.0
    for i, cid in enumerate(top_k, start=1):
        rel = ground_truth.get(cid, 0)
        gain = (2.0 ** rel) - 1.0
        discount = math.log2(i + 1.0)
        dcg += gain / discount

    # Calculate Ideal DCG (IDCG)
    all_relevances = sorted([rel for rel in ground_truth.values() if rel > 0], reverse=True)[:k]
    idcg = 0.0
    for i, rel in enumerate(all_relevances, start=1):
        gain = (2.0 ** rel) - 1.0
        discount = math.log2(i + 1.0)
        idcg += gain / discount

    if idcg <= 1e-9:
        return 0.0
    return dcg / idcg
