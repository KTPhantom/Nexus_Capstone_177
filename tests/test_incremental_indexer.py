"""
Unit tests for incremental indexer.
"""

from pathlib import Path
from nexus.cicd.incremental_indexer import IncrementalIndexer


def test_incremental_indexer_idempotence(tmp_path):
    # Setup temporary registry with 2 components
    reg_dir = tmp_path / "registry"
    student_dir = reg_dir / "student"
    student_dir.mkdir(parents=True)

    c1 = student_dir / "TestOne.tsx"
    c1.write_text("""
    import React from 'react';
    /**
     * @name TestOne
     * @domain student
     * @description Test component 1
     */
    export const TestOne = () => <div className="p-4 bg-slate-900">One</div>;
    """, encoding="utf-8")

    idx_dir = tmp_path / "vector_index"

    indexer = IncrementalIndexer(registry_dir=reg_dir, index_dir=idx_dir)

    # First run: should add 1
    stats1 = indexer.sync()
    assert len(stats1["added"]) == 1
    assert "student/TestOne" in stats1["added"]

    # Second run without changes: should be unchanged
    indexer2 = IncrementalIndexer(registry_dir=reg_dir, index_dir=idx_dir)
    stats2 = indexer2.sync()
    assert len(stats2["unchanged"]) == 1
    assert "student/TestOne" in stats2["unchanged"]

    # Third run: edit ONLY Tailwind class (cosmetic change)
    c1.write_text("""
    import React from 'react';
    /**
     * @name TestOne
     * @domain student
     * @description Test component 1
     */
    export const TestOne = () => <div className="p-8 bg-zinc-900">One</div>;
    """, encoding="utf-8")

    indexer3 = IncrementalIndexer(registry_dir=reg_dir, index_dir=idx_dir)
    stats3 = indexer3.sync()
    # Should detect cosmetic change and skip re-embedding!
    assert len(stats3["skipped_cosmetic"]) == 1
    assert "student/TestOne" in stats3["skipped_cosmetic"]
