"""
Command line runner for incremental indexing.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from nexus.cicd.incremental_indexer import IncrementalIndexer


def main():
    registry_dir = root / "registry"
    index_dir = root / "vector_index"

    print(f"Starting incremental indexer...")
    print(f"Registry: {registry_dir}")
    print(f"Output:   {index_dir}")

    indexer = IncrementalIndexer(registry_dir=registry_dir, index_dir=index_dir)
    stats = indexer.sync()

    print("\n[SYNC RESULTS]:")
    print(f"  • Added:              {len(stats['added'])} {stats['added']}")
    print(f"  • Updated:            {len(stats['updated'])} {stats['updated']}")
    print(f"  • Skipped (Cosmetic): {len(stats['skipped_cosmetic'])} {stats['skipped_cosmetic']}")
    print(f"  • Unchanged:          {len(stats['unchanged'])} {stats['unchanged']}")
    print(f"  • Deleted:            {len(stats['deleted'])} {stats['deleted']}")
    print("\nIndex synchronized successfully.")


if __name__ == "__main__":
    main()
