from pydantic import BaseModel
from typing import Dict, Any, List

class AggregateReport(BaseModel):
    system_averages: Dict[str, Dict[str, float]]
    
def compute_metrics(results: List[Dict[str, Any]]) -> AggregateReport:
    from collections import defaultdict
    sums = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)
    for r in results:
        sys = r["system"]
        sums[sys]["prompt_tokens"] += r["prompt_tokens"]
        sums[sys]["precision"] += r["precision"]
        sums[sys]["recall"] += r["recall"]
        sums[sys]["f1"] += r["f1"]
        sums[sys]["latency_ms"] += r["latency_ms"]
        counts[sys] += 1
        
    averages = {}
    for sys, sys_sums in sums.items():
        n = counts[sys]
        averages[sys] = {k: v / n for k, v in sys_sums.items()}
        
    return AggregateReport(system_averages=averages)
