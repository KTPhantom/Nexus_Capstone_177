"""
Hierarchical Navigable Small World (HNSW) Vector Index (Malkov & Yashunin 2018).
Implements multi-layer skip-list graph structure for sub-linear approximate
nearest neighbor (ANN) retrieval with cosine distance metric (Elliott & Clark 2024).
"""

import math
import random
import heapq
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
import numpy as np


class HNSWIndex:
    """
    Python/NumPy implementation of HNSW graph index.
    """

    def __init__(
        self,
        dimension: int = 384,
        M: int = 16,
        ef_construction: int = 64,
        ef_search: int = 32,
        seed: int = 42,
    ):
        self.dimension = dimension
        self.M = M
        self.M0 = 2 * M  # Max connections for layer 0
        self.ef_construction = ef_construction
        self.ef_search = ef_search
        self.mL = 1.0 / math.log(M)
        self.rng = random.Random(seed)

        # Storage
        self.vectors: Dict[str, np.ndarray] = {}  # id -> vector
        self.levels: Dict[str, int] = {}  # id -> assigned top layer
        self.graphs: List[Dict[str, List[str]]] = []  # layer -> {id: [neighbor_ids]}
        self.enter_point: Optional[str] = None
        self.max_level: int = -1

    def _cosine_distance(self, u: np.ndarray, v: np.ndarray) -> float:
        # Assumes normalized vectors; cosine distance = 1 - dot(u, v)
        dot = float(np.dot(u, v))
        return max(0.0, 1.0 - dot)

    def _random_level(self) -> int:
        # Level generation: floor(-ln(unif(0, 1)) * mL)
        r = self.rng.random()
        while r == 0:
            r = self.rng.random()
        return int(math.floor(-math.log(r) * self.mL))

    def add_item(self, item_id: str, vector: np.ndarray):
        vec = np.asarray(vector, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        else:
            vec = np.zeros(self.dimension, dtype=np.float32)

        if item_id in self.vectors:
            self.delete_item(item_id)

        target_level = self._random_level()
        self.vectors[item_id] = vec
        self.levels[item_id] = target_level

        # Expand graphs if target_level exceeds current layers
        while len(self.graphs) <= target_level:
            self.graphs.append({})

        # If index is empty
        if self.enter_point is None:
            self.enter_point = item_id
            self.max_level = target_level
            for lc in range(target_level + 1):
                self.graphs[lc][item_id] = []
            return

        curr_obj = self.enter_point
        curr_dist = self._cosine_distance(vec, self.vectors[curr_obj])

        # Phase 1: Greedy traversal from top level down to target_level + 1
        for lc in range(self.max_level, target_level, -1):
            changed = True
            while changed:
                changed = False
                neighbors = self.graphs[lc].get(curr_obj, [])
                for neighbor in neighbors:
                    d = self._cosine_distance(vec, self.vectors[neighbor])
                    if d < curr_dist:
                        curr_dist = d
                        curr_obj = neighbor
                        changed = True

        # Phase 2: For layers from min(max_level, target_level) down to 0, search layer and connect
        ep = [curr_obj]
        for lc in range(min(self.max_level, target_level), -1, -1):
            candidates = self._search_layer(vec, ep, self.ef_construction, lc)
            neighbors = self._select_neighbors(vec, candidates, self.M0 if lc == 0 else self.M)

            self.graphs[lc][item_id] = neighbors

            # Add bidirectional links
            for n in neighbors:
                self.graphs[lc].setdefault(n, [])
                if item_id not in self.graphs[lc][n]:
                    self.graphs[lc][n].append(item_id)
                max_m = self.M0 if lc == 0 else self.M
                if len(self.graphs[lc][n]) > max_m:
                    # Shrink connections
                    n_cands = [(self._cosine_distance(self.vectors[n], self.vectors[nbr]), nbr) for nbr in self.graphs[lc][n]]
                    n_cands.sort(key=lambda x: x[0])
                    seen_nbrs = set()
                    self.graphs[lc][n] = [cand[1] for cand in n_cands if not (cand[1] in seen_nbrs or seen_nbrs.add(cand[1]))][:max_m]

            ep = [c[1] for c in candidates]

        if target_level > self.max_level:
            self.max_level = target_level
            self.enter_point = item_id
            # Also init empty links for upper levels
            for lc in range(len(self.graphs)):
                if item_id not in self.graphs[lc]:
                    self.graphs[lc][item_id] = []

    def _search_layer(
        self,
        query: np.ndarray,
        enter_points: List[str],
        ef: int,
        layer: int,
    ) -> List[Tuple[float, str]]:
        visited: Set[str] = set(enter_points)
        # candidates: min-heap of (dist, id)
        candidates: List[Tuple[float, str]] = []
        # nearest: max-heap of (-dist, id) to maintain top ef items
        nearest: List[Tuple[float, str]] = []

        for ep in enter_points:
            d = self._cosine_distance(query, self.vectors[ep])
            heapq.heappush(candidates, (d, ep))
            heapq.heappush(nearest, (-d, ep))

        while candidates:
            c_dist, c_id = heapq.heappop(candidates)
            furthest_nearest = -nearest[0][0]

            if c_dist > furthest_nearest:
                break

            neighbors = self.graphs[layer].get(c_id, [])
            for nbr in neighbors:
                if nbr not in visited:
                    visited.add(nbr)
                    d = self._cosine_distance(query, self.vectors[nbr])
                    furthest_nearest = -nearest[0][0]

                    if d < furthest_nearest or len(nearest) < ef:
                        heapq.heappush(candidates, (d, nbr))
                        heapq.heappush(nearest, (-d, nbr))
                        if len(nearest) > ef:
                            heapq.heappop(nearest)

        result = [(-d, nid) for d, nid in nearest]
        result.sort(key=lambda x: x[0])
        return result

    def _select_neighbors(
        self,
        query: np.ndarray,
        candidates: List[Tuple[float, str]],
        M: int,
    ) -> List[str]:
        # Return closest M unique candidates
        candidates.sort(key=lambda x: x[0])
        seen: Set[str] = set()
        result: List[str] = []
        for _, nid in candidates:
            if nid not in seen:
                seen.add(nid)
                result.append(nid)
                if len(result) == M:
                    break
        return result

    def search_knn(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        ef: Optional[int] = None,
    ) -> List[Tuple[str, float]]:
        """
        Approximate k-NN search. Returns list of (item_id, cosine_similarity).
        """
        if self.enter_point is None or not self.vectors:
            return []

        search_ef = max(k, ef if ef is not None else self.ef_search)
        query = np.asarray(query_vector, dtype=np.float32)
        norm = np.linalg.norm(query)
        if norm > 1e-9:
            query = query / norm

        curr_obj = self.enter_point
        curr_dist = self._cosine_distance(query, self.vectors[curr_obj])

        # Phase 1: Greedy top-down search
        for lc in range(self.max_level, 0, -1):
            changed = True
            while changed:
                changed = False
                neighbors = self.graphs[lc].get(curr_obj, [])
                for nbr in neighbors:
                    d = self._cosine_distance(query, self.vectors[nbr])
                    if d < curr_dist:
                        curr_dist = d
                        curr_obj = nbr
                        changed = True

        # Phase 2: Layer 0 beam search
        candidates = self._search_layer(query, [curr_obj], search_ef, 0)
        candidates.sort(key=lambda x: x[0])

        # Return (id, similarity) where similarity = 1 - distance
        return [(item_id, max(0.0, 1.0 - dist)) for dist, item_id in candidates[:k]]

    def exact_knn(
        self,
        query_vector: np.ndarray,
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Brute-force exact k-NN search for recall benchmarking.
        """
        if not self.vectors:
            return []

        query = np.asarray(query_vector, dtype=np.float32)
        norm = np.linalg.norm(query)
        if norm > 1e-9:
            query = query / norm

        scores = []
        for item_id, vec in self.vectors.items():
            dist = self._cosine_distance(query, vec)
            sim = max(0.0, 1.0 - dist)
            scores.append((item_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

    def delete_item(self, item_id: str):
        if item_id not in self.vectors:
            return

        del self.vectors[item_id]
        self.levels.pop(item_id, None)

        for lc in range(len(self.graphs)):
            if item_id in self.graphs[lc]:
                del self.graphs[lc][item_id]
            for n in list(self.graphs[lc].keys()):
                self.graphs[lc][n] = [nbr for nbr in self.graphs[lc][n] if nbr != item_id]

        if not self.vectors:
            self.enter_point = None
            self.max_level = -1
            self.graphs = []
        else:
            self.max_level = max(self.levels.values())
            # Clean up empty upper levels if max_level decreased
            while len(self.graphs) > self.max_level + 1:
                self.graphs.pop()

            # Ensure enter_point is valid, exists in self.vectors, and is present at max_level
            if (
                self.enter_point == item_id
                or self.enter_point not in self.vectors
                or self.levels.get(self.enter_point, -1) < self.max_level
            ):
                top_candidates = [k for k, lvl in self.levels.items() if lvl == self.max_level]
                self.enter_point = top_candidates[0] if top_candidates else next(iter(self.vectors))

    def save(self, filepath: str | Path):
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dimension": self.dimension,
            "M": self.M,
            "M0": self.M0,
            "ef_construction": self.ef_construction,
            "ef_search": self.ef_search,
            "mL": self.mL,
            "enter_point": self.enter_point,
            "max_level": self.max_level,
            "levels": self.levels,
            "graphs": self.graphs,
            "vectors": {k: v.tolist() for k, v in self.vectors.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    @classmethod
    def load(cls, filepath: str | Path) -> "HNSWIndex":
        path = Path(filepath)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        idx = cls(
            dimension=data["dimension"],
            M=data["M"],
            ef_construction=data["ef_construction"],
            ef_search=data["ef_search"],
        )
        idx.enter_point = data["enter_point"]
        idx.max_level = data["max_level"]
        idx.levels = data["levels"]
        idx.graphs = data["graphs"]
        idx.vectors = {k: np.array(v, dtype=np.float32) for k, v in data["vectors"].items()}
        return idx
