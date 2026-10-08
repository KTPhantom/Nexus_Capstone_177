"""
Retrieval Quality Regression Gate.
Enforces strict performance and latency thresholds in CI/CD pipeline
prior to publishing component embeddings to production vector stores.
"""

import sys
from pathlib import Path
from typing import Dict, Any

from nexus.evaluation.benchmark_runner import BenchmarkRunner
from nexus.evaluation.dataset import GOLDEN_BENCHMARK_DATASET


class QualityGateThresholds:
    MIN_MRR: float = 0.85
    MIN_RECALL_AT_3: float = 0.90
    MIN_NDCG_AT_5: float = 0.85
    MAX_MEAN_LATENCY_MS: float = 50.0


def run_regression_gate(
    registry_dir: str | Path = "registry",
    thresholds: QualityGateThresholds = QualityGateThresholds(),
) -> bool:
    print("=" * 65)
    print("  NEXUS CI/CD: RETRIEVAL QUALITY REGRESSION GATE")
    print("=" * 65)

    runner = BenchmarkRunner(registry_dir=registry_dir)
    results = runner.run_benchmark(GOLDEN_BENCHMARK_DATASET)
    nexus_metrics = results["Proposed Nexus Component Pipeline"]

    print(f"\n[EVALUATION METRICS]:")
    print(f"  • MRR:             {nexus_metrics.mrr:.4f}  (Threshold: >= {thresholds.MIN_MRR:.2f})")
    print(f"  • Recall@3:        {nexus_metrics.recall_at_3:.4f}  (Threshold: >= {thresholds.MIN_RECALL_AT_3:.2f})")
    print(f"  • NDCG@5:          {nexus_metrics.ndcg_at_5:.4f}  (Threshold: >= {thresholds.MIN_NDCG_AT_5:.2f})")
    print(f"  • Mean Latency:    {nexus_metrics.mean_latency_ms:.2f} ms  (Threshold: <= {thresholds.MAX_MEAN_LATENCY_MS:.1f} ms)")
    print(f"  • P95 Latency:     {nexus_metrics.p95_latency_ms:.2f} ms")

    failures = []
    if nexus_metrics.mrr < thresholds.MIN_MRR:
        failures.append(f"MRR {nexus_metrics.mrr:.4f} < {thresholds.MIN_MRR}")
    if nexus_metrics.recall_at_3 < thresholds.MIN_RECALL_AT_3:
        failures.append(f"Recall@3 {nexus_metrics.recall_at_3:.4f} < {thresholds.MIN_RECALL_AT_3}")
    if nexus_metrics.ndcg_at_5 < thresholds.MIN_NDCG_AT_5:
        failures.append(f"NDCG@5 {nexus_metrics.ndcg_at_5:.4f} < {thresholds.MIN_NDCG_AT_5}")
    if nexus_metrics.mean_latency_ms > thresholds.MAX_MEAN_LATENCY_MS:
        failures.append(f"Mean Latency {nexus_metrics.mean_latency_ms:.2f}ms > {thresholds.MAX_MEAN_LATENCY_MS}ms")

    print("\n" + "-" * 65)
    if failures:
        print("[GATE FAILED]: Retrieval quality regressed below permitted criteria!")
        for fail in failures:
            print(f"   - VIOLATION: {fail}")
        print("CI/CD pipeline execution blocked.")
        return False
    else:
        print("[GATE PASSED]: All retrieval accuracy and latency constraints satisfied.")
        print("Vector index is verified healthy and ready for deployment.")
        return True


if __name__ == "__main__":
    passed = run_regression_gate()
    sys.exit(0 if passed else 1)
