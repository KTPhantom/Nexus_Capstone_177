"""
Unit tests for CI/CD regression gate.
"""

from nexus.cicd.regression_gate import run_regression_gate, QualityGateThresholds


def test_regression_gate_passes_on_current_registry():
    # Test that current registry passes quality gate with standard thresholds
    thresholds = QualityGateThresholds()
    thresholds.MIN_MRR = 0.85
    thresholds.MIN_RECALL_AT_3 = 0.90
    thresholds.MIN_NDCG_AT_5 = 0.85

    passed = run_regression_gate(thresholds=thresholds)
    assert passed is True
