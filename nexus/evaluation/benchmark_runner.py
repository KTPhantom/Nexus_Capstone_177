"""
Comparative Benchmark Runner.
Executes automated comparative evaluation between:
1. BM25 Lexical Baseline
2. Naive Raw Code Dense Embedding
3. Proposed Nexus Component Pipeline (AST + Noise Filter + Composite Embeddings + HNSW + MMR)
"""

import time
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np

from nexus.parser.ast_engine import TSXComponentParser
from nexus.indexing.embedder import DenseEmbedder
from nexus.retrieval.engine import RetrievalEngine
from .dataset import GOLDEN_BENCHMARK_DATASET, EvaluationQuery
from .metrics import BenchmarkMetrics, recall_at_k, reciprocal_rank, ndcg_at_k


class BenchmarkRunner:
    def __init__(self, registry_dir: str | Path = "registry"):
        self.registry_dir = Path(registry_dir)
        self.parser = TSXComponentParser()
        self.embedder = DenseEmbedder()
        self.engine = RetrievalEngine(embedder=self.embedder)

        self._setup_indices()

    def _setup_indices(self):
        files = list(self.registry_dir.glob("*/*.tsx"))
        parsed_components = []
        raw_sources = {}

        for f in files:
            meta = self.parser.parse_file(f)
            parsed_components.append(meta)
            with open(f, "r", encoding="utf-8") as src_f:
                raw_sources[meta.component_id] = src_f.read()

        self.engine.index_components(parsed_components, raw_sources)

    def run_benchmark(self, queries: List[EvaluationQuery] = GOLDEN_BENCHMARK_DATASET) -> Dict[str, BenchmarkMetrics]:
        results = {}

        # 1. Evaluate BM25
        results["BM25 Lexical Baseline"] = self._evaluate_pipeline(
            name="BM25 Lexical Baseline",
            search_fn=lambda q: [cid for cid, _ in self.engine.search_bm25(q, top_k=5)],
            queries=queries,
        )

        # 2. Evaluate Naive Raw Code Dense Embedding
        results["Naive Raw Code Dense Embedding"] = self._evaluate_pipeline(
            name="Naive Raw Code Dense Embedding",
            search_fn=lambda q: [cid for cid, _ in self.engine.search_naive_dense(q, top_k=5)],
            queries=queries,
        )

        # 3. Evaluate Proposed Nexus Component Pipeline
        results["Proposed Nexus Component Pipeline"] = self._evaluate_pipeline(
            name="Proposed Nexus Component Pipeline",
            search_fn=lambda q: [res.component_id for res in self.engine.search_nexus(q, top_k=5, use_mmr=True, lambda_param=0.75)],
            queries=queries,
        )

        return results

    def _evaluate_pipeline(self, name: str, search_fn, queries: List[EvaluationQuery]) -> BenchmarkMetrics:
        r1_list = []
        r3_list = []
        r5_list = []
        mrr_list = []
        ndcg_list = []
        latencies = []

        # Warm-up run
        for q in queries[:2]:
            search_fn(q.query_text)

        for q in queries:
            t0 = time.perf_counter()
            retrieved_ids = search_fn(q.query_text)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed_ms)

            gt = q.relevant_components
            r1_list.append(recall_at_k(retrieved_ids, gt, k=1))
            r3_list.append(recall_at_k(retrieved_ids, gt, k=3))
            r5_list.append(recall_at_k(retrieved_ids, gt, k=5))
            mrr_list.append(reciprocal_rank(retrieved_ids, gt))
            ndcg_list.append(ndcg_at_k(retrieved_ids, gt, k=5))

        latencies_arr = np.array(latencies)
        return BenchmarkMetrics(
            pipeline_name=name,
            recall_at_1=float(np.mean(r1_list)),
            recall_at_3=float(np.mean(r3_list)),
            recall_at_5=float(np.mean(r5_list)),
            mrr=float(np.mean(mrr_list)),
            ndcg_at_5=float(np.mean(ndcg_list)),
            mean_latency_ms=float(np.mean(latencies_arr)),
            p95_latency_ms=float(np.percentile(latencies_arr, 95)),
        )

    def generate_markdown_report(self, results: Dict[str, BenchmarkMetrics]) -> str:
        report = []
        report.append("# Nexus Component Retrieval Benchmark Evaluation Report")
        report.append("")
        report.append("## Executive Summary of Comparative Performance")
        report.append("")
        report.append("| Pipeline | Recall@1 | Recall@3 | Recall@5 | MRR | NDCG@5 | Mean Latency (ms) | P95 Latency (ms) |")
        report.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

        for name, m in results.items():
            report.append(
                f"| **{m.pipeline_name}** | {m.recall_at_1:.3f} | {m.recall_at_3:.3f} | {m.recall_at_5:.3f} | {m.mrr:.3f} | {m.ndcg_at_5:.3f} | {m.mean_latency_ms:.2f} ms | {m.p95_latency_ms:.2f} ms |"
            )

        report.append("")
        report.append("### Key Statistical Observations")
        nexus_m = results["Proposed Nexus Component Pipeline"]
        naive_m = results["Naive Raw Code Dense Embedding"]
        bm25_m = results["BM25 Lexical Baseline"]

        mrr_gain_naive = ((nexus_m.mrr - naive_m.mrr) / max(1e-9, naive_m.mrr)) * 100.0
        mrr_gain_bm25 = ((nexus_m.mrr - bm25_m.mrr) / max(1e-9, bm25_m.mrr)) * 100.0
        ndcg_gain_naive = ((nexus_m.ndcg_at_5 - naive_m.ndcg_at_5) / max(1e-9, naive_m.ndcg_at_5)) * 100.0

        sign_mrr_naive = "+" if mrr_gain_naive >= 0 else ""
        sign_mrr_bm25 = "+" if mrr_gain_bm25 >= 0 else ""
        sign_ndcg_naive = "+" if ndcg_gain_naive >= 0 else ""

        report.append(f"- **MRR Performance**: Nexus achieves MRR of **{nexus_m.mrr:.3f}** ({sign_mrr_naive}{mrr_gain_naive:.1f}% vs Naive Dense, {sign_mrr_bm25}{mrr_gain_bm25:.1f}% vs BM25).")
        report.append(f"- **NDCG@5 Ranking Quality**: Nexus achieves an NDCG@5 of **{nexus_m.ndcg_at_5:.3f}** ({sign_ndcg_naive}{ndcg_gain_naive:.1f}% vs Naive Dense).")
        report.append(f"- **Sub-linear Search Latency**: With HNSW indexing, mean retrieval latency is **{nexus_m.mean_latency_ms:.2f} ms**, fully capable of real-time interactive multi-agent workspace composition.")
        report.append("")
        return "\n".join(report)


if __name__ == "__main__":
    runner = BenchmarkRunner()
    results = runner.run_benchmark()
    print(runner.generate_markdown_report(results))
