"""
Maximal Marginal Relevance (MMR) Diversity Re-ranker.
Academic Foundation: APIRec (Springer 2024 - API Recommendation with Knowledge Graph Embeddings and MMR Re-ranking).
Mitigates tool redundancy and maximizes capability coverage across retrieved workspace components.
"""

from typing import List, Dict, Tuple, Optional, Any
import numpy as np


class APIRecMMRReranker:
    """
    APIRec MMR re-ranking algorithm.
    Balances query relevance against inter-component redundancy.
    """

    def __init__(self, lambda_param: float = 0.75):
        """
        lambda_param (float): Trade-off parameter in [0.0, 1.0].
            1.0 = Pure relevance (no diversity penalty).
            0.0 = Pure diversity (maximum dissimilarity to already chosen components).
            0.75 = Optimal APIRec baseline balancing semantic relevance and tool variety.
        """
        self.lambda_param = lambda_param

    @staticmethod
    def _cosine_sim(u: Optional[np.ndarray], v: Optional[np.ndarray]) -> float:
        if u is None or v is None:
            return 0.0
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
        if norm_u < 1e-9 or norm_v < 1e-9:
            return 0.0
        return float(np.dot(u, v) / (norm_u * norm_v))

    def rerank(
        self,
        query_vector: np.ndarray,
        candidate_ids: List[str],
        candidate_vectors: Dict[str, np.ndarray],
        candidate_scores: Dict[str, float],
        top_k: int = 5,
        capabilities_map: Optional[Dict[str, List[str]]] = None,
        lambda_override: Optional[float] = None,
    ) -> List[Tuple[str, float]]:
        """
        Execute MMR re-ranking on candidate components.
        Returns: List of (component_id, mmr_score) sorted in descending rank order.
        """
        lam = self.lambda_param if lambda_override is None else lambda_override

        if not candidate_ids:
            return []

        remaining = set(candidate_ids)
        selected: List[str] = []
        selected_scores: List[Tuple[str, float]] = []

        target_k = min(top_k, len(candidate_ids))

        while len(selected) < target_k and remaining:
            best_id: Optional[str] = None
            best_mmr_score: float = -float("inf")

            for cid in remaining:
                relevance = candidate_scores.get(
                    cid,
                    self._cosine_sim(query_vector, candidate_vectors.get(cid)),
                )

                if not selected:
                    # First item is purely highest relevance
                    mmr_score = relevance
                else:
                    # Max similarity to already selected items
                    vec_cid = candidate_vectors.get(cid)
                    max_sim_to_selected = max(
                        self._cosine_sim(vec_cid, candidate_vectors.get(sel_id))
                        for sel_id in selected
                    ) if selected else 0.0

                    # Optional capability overlap penalty (APIRec knowledge graph heuristic)
                    cap_overlap_penalty = 0.0
                    if capabilities_map and cid in capabilities_map:
                        curr_caps = set(capabilities_map[cid])
                        for sel_id in selected:
                            sel_caps = set(capabilities_map.get(sel_id, []))
                            if curr_caps and sel_caps:
                                jaccard = len(curr_caps & sel_caps) / len(curr_caps | sel_caps)
                                cap_overlap_penalty = max(cap_overlap_penalty, jaccard * (1.0 - lam) * 0.15)

                    mmr_score = lam * relevance - (1.0 - lam) * max_sim_to_selected - cap_overlap_penalty

                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_id = cid

            if best_id is not None:
                selected.append(best_id)
                remaining.remove(best_id)
                selected_scores.append((best_id, float(best_mmr_score)))

        return selected_scores
