"""
Command line runner for CI/CD retrieval quality regression gate.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from nexus.cicd.regression_gate import run_regression_gate


def main():
    registry_dir = root / "registry"
    passed = run_regression_gate(registry_dir=registry_dir)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
