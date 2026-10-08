"""
Command line runner for comparative benchmark evaluation.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from nexus.evaluation.benchmark_runner import BenchmarkRunner


def main():
    registry_dir = root / "registry"

    runner = BenchmarkRunner(registry_dir=registry_dir)
    results = runner.run_benchmark()
    report = runner.generate_markdown_report(results)
    print(report)


if __name__ == "__main__":
    main()
