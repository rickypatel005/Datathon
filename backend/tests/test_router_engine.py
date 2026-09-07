"""
Unit and integration tests for Person 1: Intelligent Dataset & Task Router Engine (Phase 1D).
"""
import pytest
import pandas as pd
import numpy as np
import json

from app.contracts.discovery import (
    RouterDecision,
    TaskRouteDecision,
    DatasetFingerprint,
    TargetCandidate,
    QualityReport,
    LeakageReport,
    TaskType,
    ValidationStrategy,
    DiscoveryContract,
)
from app.pipeline.router import route_dataset
from app.pipeline.fingerprint import generate_fingerprint
from app.pipeline.quality import evaluate_quality
from app.pipeline.leakage import detect_leakage
from app.pipeline.discovery import run_discovery


def test_1_binary_classification_routing():
    """Test 1: Binary classification target routes to StratifiedKFold with classification championship and balanced metrics."""
    df = pd.DataFrame({
        "age": [20 + (i % 40) for i in range(100)],
        "salary": [30000.0 + i * 500 for i in range(100)],
        "churn": [1 if i % 4 == 0 else 0 for i in range(100)],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task == TaskType.BINARY_CLASSIFICATION
    assert decision.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD
    assert "classification_championship" in decision.applicable_engines
    assert "roc_auc" in decision.recommended_metrics
    assert "pr_auc" in decision.recommended_metrics
    assert decision.task_decisions["binary_classification"].status == "applicable"
    assert decision.task_decisions["regression"].status == "skipped"


def test_2_multiclass_classification_routing():
    """Test 2: Multiclass categorical target (3+ classes) routes to Multiclass Classification with StratifiedKFold."""
    df = pd.DataFrame({
        "feature_1": [10.0 + (i % 30) for i in range(120)],
        "feature_2": [50.0 + (i % 10) for i in range(120)],
        "target_tier": ["Bronze", "Silver", "Gold"] * 40,
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task == TaskType.MULTICLASS_CLASSIFICATION
    assert decision.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD
    assert "classification_championship" in decision.applicable_engines
    assert "f1_weighted" in decision.recommended_metrics
    assert decision.task_decisions["multiclass_classification"].status == "applicable"


def test_3_regression_routing():
    """Test 3: Continuous numeric target routes to Regression with KFold and RMSE/R2 metrics."""
    df = pd.DataFrame({
        "experience": [1.0 + (i % 20) for i in range(100)],
        "education_level": [i % 4 for i in range(100)],
        "salary": [45000.0 + i * 1250.0 for i in range(100)], # continuous numeric target
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task == TaskType.REGRESSION
    assert decision.validation_strategy == ValidationStrategy.K_FOLD
    assert "regression_engine" in decision.applicable_engines
    assert "rmse" in decision.recommended_metrics
    assert "r2_score" in decision.recommended_metrics
    assert decision.task_decisions["regression"].status == "applicable"


def test_4_forecasting_routing():
    """Test 4: Ordered temporal structure with sufficient history routes to TimeSeriesSplit and forecasting engine."""
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "temperature": [20.0 + (i % 15) for i in range(60)],
        "electricity_demand": [500.0 + i * 3.5 for i in range(60)],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands, temporal=fingerprint.temporal)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert "time_series_forecasting" in decision.applicable_engines
    assert decision.validation_strategy == ValidationStrategy.TIME_SERIES_SPLIT
    assert decision.task_decisions["time_series_forecasting"].status == "applicable"


def test_5_clustering_routing():
    """Test 5: Dataset without supervised target routes to Clustering and Unsupervised EDA."""
    df = pd.DataFrame({
        "num_1": [1.0, 2.0, 3.0, 4.0, 5.0] * 10,
        "num_2": [10.0, 20.0, 30.0, 40.0, 50.0] * 10,
        "cat_1": ["A", "B", "C", "D", "E"] * 10,
    })
    fingerprint, columns_meta, _ = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_candidates=[])

    # No target candidates
    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=[],
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task == TaskType.CLUSTERING
    assert "clustering_engine" in decision.applicable_engines
    assert "silhouette_score" in decision.recommended_metrics
    assert decision.task_decisions["clustering"].status == "applicable"


def test_6_descriptive_only_dataset():
    """Test 6: Tabular dataset always includes descriptive statistics and statistical profiling."""
    df = pd.DataFrame({
        "col_a": [1, 2, 3, 4, 5],
        "col_b": ["x", "y", "z", "w", "v"],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        columns_meta=columns_meta,
    )

    assert "statistical_engine" in decision.applicable_engines
    assert decision.task_decisions["descriptive_statistics"].status == "applicable"


def test_7_no_target_dataset():
    """Test 7: Router handles no-target dataset safely without inventing a fake target."""
    df = pd.DataFrame({
        "val_1": [i % 7 for i in range(40)],
        "val_2": [i * 2.5 for i in range(40)],
    })
    fingerprint, columns_meta, _ = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=[],
        quality_report=quality_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task in (TaskType.CLUSTERING, TaskType.UNSUPERVISED_EDA)
    assert decision.task_decisions["binary_classification"].status == "skipped"
    assert decision.task_decisions["regression"].status == "skipped"


def test_8_multiple_target_ambiguity():
    """Test 8: Multiple target candidates are preserved in secondary/task evidence without crash."""
    df = pd.DataFrame({
        "user_id": [f"U_{i}" for i in range(80)],
        "churn": [0, 1] * 40,
        "revenue": [100.0 + i * 10 for i in range(80)],
        "segment": ["SMB", "Enterprise"] * 40,
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task == TaskType.BINARY_CLASSIFICATION
    assert len(decision.secondary_tasks) >= 1


def test_9_leakage_aware_feature_partition():
    """Test 9: Excluded leakage columns and identifiers are strictly partitioned from usable_feature_columns."""
    df = pd.DataFrame({
        "customer_id": [f"CUST_{i}" for i in range(100)], # Identifier
        "post_event_recovery": [0.0 if i % 2 == 0 else 500.0 for i in range(100)], # Post event leak
        "target": [0, 1] * 50,
        "legit_feature_1": [10.0 + (i % 30) for i in range(100)],
        "legit_feature_2": (["A", "B", "C"] * 33) + ["A"],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert "customer_id" in decision.excluded_identifier_columns
    assert "post_event_recovery" in decision.excluded_leakage_columns
    assert "legit_feature_1" in decision.usable_feature_columns
    assert "legit_feature_2" in decision.usable_feature_columns
    assert "customer_id" not in decision.usable_feature_columns
    assert "post_event_recovery" not in decision.usable_feature_columns
    assert "target" not in decision.usable_feature_columns


def test_10_identifier_only_dataset():
    """Test 10: Identifier-only dataset leaves 0 usable features, triggering insufficient_evidence for clustering/correlation."""
    df = pd.DataFrame({
        "id_1": [f"ID1_{i}" for i in range(30)],
        "id_2": [f"ID2_{i}" for i in range(30)],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert len(decision.usable_feature_columns) == 0
    assert decision.task_decisions["correlation_analysis"].status == "insufficient_evidence"
    assert decision.task_decisions["clustering"].status == "insufficient_evidence"


def test_11_severe_class_imbalance():
    """Test 11: Severe class imbalance triggers PR-AUC and Balanced Accuracy metrics with StratifiedKFold."""
    df = pd.DataFrame({
        "feat_1": [i % 25 for i in range(100)],
        "rare_event": [1] * 3 + [0] * 97,  # 3% positive class
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD
    assert "pr_auc" in decision.recommended_metrics
    assert "balanced_accuracy" in decision.recommended_metrics


def test_12_insufficient_temporal_history():
    """Test 12: Datetime column with < 10 distinct dates yields insufficient_evidence for forecasting."""
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5, freq="D"), # Only 5 dates
        "sales": [100, 110, 105, 120, 115],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands, temporal=fingerprint.temporal)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.task_decisions["time_series_forecasting"].status == "insufficient_evidence"
    assert "fewer than minimum distinct timestamps" in decision.task_decisions["time_series_forecasting"].reason


def test_13_grouped_data_validation_route():
    """Test 13: Grouped data with a recognized group variable (e.g. hospital_id, store_id) routes to GroupKFold."""
    df = pd.DataFrame({
        "hospital_id": [f"HOSP_{i % 5}" for i in range(100)], # 5 distinct hospital groups
        "feature_x": [10.0 + (i % 30) for i in range(100)],
        "target": [0, 1] * 50,
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert decision.validation_strategy == ValidationStrategy.GROUP_K_FOLD
    assert decision.group_column == "hospital_id"


def test_14_usable_vs_excluded_feature_lists():
    """Test 14: Clear separation of usable, identifier, leakage, review, and unsupported features."""
    df = pd.DataFrame({
        "id": [f"ID_{i}" for i in range(60)],
        "target": [0, 1] * 30,
        "constant_col": [99] * 60,
        "usable_num": [10.0 + (i % 15) for i in range(60)],
        "usable_cat": ["A", "B", "C"] * 20,
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        leakage_report=leakage_rep,
        columns_meta=columns_meta,
    )

    assert "id" in decision.excluded_identifier_columns
    assert "constant_col" in decision.unsupported_feature_columns
    assert set(decision.usable_feature_columns) == {"usable_num", "usable_cat"}


def test_15_empty_dataset_handling():
    """Test 15: Empty datasets (0 rows) return structured decisions without exceptions."""
    df = pd.DataFrame(columns=["a", "b", "c"])
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        columns_meta=columns_meta,
    )

    assert decision.recommended_primary_task == TaskType.UNSUPERVISED_EDA
    assert decision.task_decisions["descriptive_statistics"].status == "insufficient_evidence"


def test_16_insufficient_evidence_state():
    """Test 16: Explicit insufficient_evidence state when prerequisites for a capability are not met."""
    df = pd.DataFrame({"single_col": [1, 2, 3, 4, 5]})
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)

    decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_cands,
        quality_report=quality_rep,
        columns_meta=columns_meta,
    )

    assert decision.task_decisions["correlation_analysis"].status == "insufficient_evidence"


def test_17_deterministic_repeated_routing():
    """Test 17: Repeated routing on identical inputs yields identical decisions and rationale."""
    df = pd.DataFrame({
        "feat_a": [i % 10 for i in range(50)],
        "feat_b": [i * 1.5 for i in range(50)],
        "target": [0, 1] * 25,
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    quality_rep, _, _ = evaluate_quality(df, columns_meta)
    leakage_rep = detect_leakage(df, columns_meta, target_cands)

    d1 = route_dataset(fingerprint, target_cands, quality_rep, leakage_rep, columns_meta)
    d2 = route_dataset(fingerprint, target_cands, quality_rep, leakage_rep, columns_meta)

    assert d1.recommended_primary_task == d2.recommended_primary_task
    assert d1.validation_strategy == d2.validation_strategy
    assert d1.applicable_engines == d2.applicable_engines
    assert d1.usable_feature_columns == d2.usable_feature_columns
    assert d1.rationale == d2.rationale


def test_18_json_serialization_and_contract_compatibility(tmp_path):
    """Test 18: DiscoveryContract with RouterDecision passes full JSON round-trip serialization."""
    csv_file = tmp_path / "router_test.csv"
    df = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(50)],
        "age": [20 + (i % 40) for i in range(50)],
        "income": [40000.0 + i * 500 for i in range(50)],
        "default": [1 if i % 5 == 0 else 0 for i in range(50)],
    })
    df.to_csv(csv_file, index=False)

    contract = run_discovery(str(csv_file))

    assert isinstance(contract, DiscoveryContract)
    assert contract.router.recommended_primary_task == TaskType.BINARY_CLASSIFICATION
    assert len(contract.router.usable_feature_columns) == 2

    # JSON Round-trip
    dumped = contract.model_dump()
    json_str = json.dumps(dumped, default=str)
    reparsed = DiscoveryContract.model_validate(json.loads(json_str))

    assert reparsed.router.recommended_primary_task == contract.router.recommended_primary_task
    assert reparsed.router.validation_strategy == contract.router.validation_strategy
    assert reparsed.router.usable_feature_columns == contract.router.usable_feature_columns


def test_19_contract_mock_fixture_compatibility():
    """Test 19: Existing discovery_mock.json fixture remains valid and conformant."""
    with open("backend/app/contracts/fixtures/discovery_mock.json", "r") as f:
        data = json.load(f)
    contract = DiscoveryContract.model_validate(data)
    assert contract.router.recommended_primary_task == TaskType.BINARY_CLASSIFICATION
    assert contract.router.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD
