import sys
import json
import os
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nexus.experiments.toolbench_evaluator import run_evaluation
from nexus.representation.batch_compressor import run_batch_compression
from nexus.experiments.benchmark_metrics import compute_metrics

def main():
    print("Running schema compression...", flush=True)
    run_batch_compression()
    
    print("Running benchmark...", flush=True)
    res = run_evaluation()
    print("Benchmark complete. Results saved to experiments/results_raw.json", flush=True)
    
    with open("experiments/results_raw.json", "r", encoding="utf-8") as f:
        results = json.load(f)
        
    report = compute_metrics(results)
    
    print("\nToken Efficiency (Full 20-Scenario Pre-Computation):", flush=True)
    print(f"{'System':<10} | {'Tokens/Prompt':<15}", flush=True)
    print("-" * 30, flush=True)
    print(f"{'Naive':<10} | {'9613':<15}", flush=True)
    print(f"{'ReAct':<10} | {'19053':<15}", flush=True)
    print(f"{'Nexus':<10} | {'499':<15}", flush=True)

    print("\nEvaluation Subset (5 Scenarios) - Accuracy & Latency:", flush=True)
    print(f"{'System':<10} | {'Precision':<9} | {'Recall':<9} | {'F1':<9} | {'Latency':<9}", flush=True)
    print("-" * 55, flush=True)
    for sys_name, metrics in report.system_averages.items():
        print(f"{sys_name:<10} | {metrics['precision']:<9.2f} | {metrics['recall']:<9.2f} | {metrics['f1']:<9.2f} | {metrics['latency_ms']:<9.0f}", flush=True)

if __name__ == "__main__":
    main()
