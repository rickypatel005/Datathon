"""
Unit and integration tests for Person 1: Leakage Hunter & Identifier Isolation Engine (Phase 1C).
"""
import pytest
import pandas as pd
import numpy as np
import json

from app.contracts.discovery import (
    LeakageReport,
    LeakageCandidate,
    LeakageType,
    LeakageRiskLevel,
    LeakageRecommendation,
    IdentifierIsolation,
    ColumnMetadata,
    TargetCandidate,
    InferredDtype,
    TaskType,
    DiscoveryContract,
)
from app.pipeline.leakage import (
    detect_leakage,
    isolate_identifiers,
    detect_target_derived_and_post_event,
    detect_temporal_and_future_leakage,
    calculate_cramers_v,
    calculate_correlation_ratio,
    check_exact_or_inverse_copy,
)
from app.pipeline.fingerprint import generate_fingerprint
from app.pipeline.discovery import run_discovery


def test_1_direct_target_copy():
    """Test 1: Exact identical copy of target is detected as CRITICAL TARGET_DERIVED leakage."""
    df = pd.DataFrame({
        "target": [0, 1, 0, 1, 0, 1, 1, 0] * 10,
        "target_copy": [0, 1, 0, 1, 0, 1, 1, 0] * 10,
        "feature_x": [10, 20, 30, 40, 50, 60, 70, 80] * 10,
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    assert report.has_leakage_risk is True
    copy_finding = next((f for f in report.findings if f.column == "target_copy"), None)
    assert copy_finding is not None
    assert copy_finding.leakage_type == LeakageType.TARGET_DERIVED
    assert copy_finding.risk_level == LeakageRiskLevel.CRITICAL
    assert copy_finding.confidence == 1.0
    assert copy_finding.recommendation == "exclude_from_model"
    assert "target_copy" in report.recommended_drops


def test_2_target_complement_transformation():
    """Test 2: Binary 1-complement (inverse) of target is detected as CRITICAL TARGET_DERIVED leakage."""
    target_vals = [0, 1, 0, 1, 1, 0, 0, 1] * 10
    df = pd.DataFrame({
        "churn": target_vals,
        "retained": [1 - v for v in target_vals],
        "tenure": [1, 2, 3, 4, 5, 6, 7, 8] * 10,
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    retained_finding = next((f for f in report.findings if f.column == "retained"), None)
    assert retained_finding is not None
    assert retained_finding.leakage_type == LeakageType.TARGET_DERIVED
    assert retained_finding.risk_level == LeakageRiskLevel.CRITICAL
    assert retained_finding.recommendation == "exclude_from_model"
    assert "retained" in report.recommended_drops


def test_3_target_derived_encoded_feature():
    """Test 3: Feature containing target name with high correlation is flagged as TARGET_DERIVED."""
    df = pd.DataFrame({
        "default": [0, 1, 0, 1, 0, 1, 1, 0] * 15,
        "default_flag": [0.0, 0.95, 0.05, 0.90, 0.0, 1.0, 0.98, 0.02] * 15,
        "income": [50000 + i * 100 for i in range(120)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    cand = next((f for f in report.findings if f.column == "default_flag"), None)
    assert cand is not None
    assert cand.leakage_type == LeakageType.TARGET_DERIVED
    assert cand.risk_level in (LeakageRiskLevel.HIGH, LeakageRiskLevel.CRITICAL)
    assert "default_flag" in report.recommended_drops


def test_4_suspicious_target_naming():
    """Test 4: Columns embedding target name are audited against target."""
    df = pd.DataFrame({
        "fraud": [0, 1, 0, 0, 1, 0, 0, 0] * 15,
        "fraud_risk_score": [0.1, 0.9, 0.2, 0.15, 0.85, 0.1, 0.2, 0.05] * 15,
        "amount": [100.0 + i for i in range(120)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    cand = next((f for f in report.findings if f.column == "fraud_risk_score"), None)
    assert cand is not None
    assert cand.leakage_type in (LeakageType.TARGET_DERIVED, LeakageType.SUSPICIOUS_PREDICTIVE, LeakageType.SUSPICIOUS_CORRELATION)
    assert cand.recommendation in ("exclude_from_model", "review")


def test_5_post_event_feature():
    """Test 5: Post-event collection fields (e.g. collection_status, recovery_amount) are flagged."""
    df = pd.DataFrame({
        "loan_default": [0, 1, 0, 1, 0, 0, 1, 0] * 15,
        "collection_status": ["None", "Active", "None", "Settled", "None", "None", "Active", "None"] * 15,
        "recovery_amount": [0.0, 1500.0, 0.0, 3000.0, 0.0, 0.0, 500.0, 0.0] * 15,
        "credit_score": [700, 550, 720, 580, 690, 750, 540, 710] * 15,
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    post_event_cols = [f.column for f in report.findings if f.leakage_type == LeakageType.POST_EVENT]
    assert "collection_status" in post_event_cols
    assert "recovery_amount" in post_event_cols
    assert "recovery_amount" in report.recommended_drops


def test_6_future_timestamp_feature():
    """Test 6: Secondary timestamp occurring systematically after event date is flagged as FUTURE leakage."""
    event_dates = pd.date_range("2023-01-01", periods=60, freq="D")
    settle_dates = [d + pd.Timedelta(days=30) for d in event_dates]
    df = pd.DataFrame({
        "event_date": event_dates,
        "settlement_date": settle_dates,
        "sales": [100.0 + (i % 10) for i in range(60)],
        "target": [0 if i % 3 == 0 else 1 for i in range(60)],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands, temporal=fingerprint.temporal)

    future_findings = [f for f in report.findings if f.leakage_type == LeakageType.FUTURE]
    assert len(future_findings) >= 1
    assert any(f.column == "settlement_date" for f in future_findings)


def test_7_normal_time_column_not_flagged():
    """Test 7: Primary time column used for time series is NOT falsely marked as future leakage."""
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "temperature": [20.0 + (i % 10) for i in range(50)],
        "demand": [100.0 + i * 2.5 for i in range(50)],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands, temporal=fingerprint.temporal)

    future_cols = [f.column for f in report.findings if f.leakage_type == LeakageType.FUTURE]
    assert "timestamp" not in future_cols


def test_8_strongly_correlated_legitimate_feature():
    """Test 8: Strongly correlated legitimate feature is NOT marked confirmed leakage, but warned/reviewed."""
    # Synthetic realistic relationship with r ~ 0.88
    np.random.seed(42)
    x = np.linspace(10, 100, 100)
    noise = np.random.normal(0, 8, 100)
    y = x * 1.5 + noise

    df = pd.DataFrame({
        "credit_history_score": x,
        "approved_credit_limit": y,
        "age": np.random.randint(20, 65, 100),
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    score_finding = next((f for f in report.findings if f.column == "credit_history_score"), None)
    if score_finding is not None:
        # Must be suspicious predictive / warning, NOT critical target copy
        assert score_finding.risk_level in (LeakageRiskLevel.MEDIUM, LeakageRiskLevel.HIGH)
        assert score_finding.leakage_type == LeakageType.SUSPICIOUS_PREDICTIVE
        assert score_finding.recommendation in ("use_with_warning", "review")


def test_9_uuid_identifier_isolation():
    """Test 9: UUID identifiers are isolated with structured recommendations to exclude from models."""
    df = pd.DataFrame({
        "session_id": [f"12345678-1234-5678-1234-{i:012d}" for i in range(60)],
        "clicks": [i % 10 for i in range(60)],
        "converted": [1 if i % 4 == 0 else 0 for i in range(60)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    assert len(report.identifiers) == 1
    assert report.identifiers[0].column == "session_id"
    assert report.identifiers[0].recommended_use == "exclude_from_model"
    assert "session_id" in report.recommended_drops
    assert "session_id" not in report.sanitized_feature_columns


def test_10_sequential_identifier_isolation():
    """Test 10: Sequential IDs (e.g. 1001, 1002, 1003) are isolated."""
    df = pd.DataFrame({
        "user_id": range(1001, 1061),
        "balance": [500.0 + i for i in range(60)],
        "churn": [0 if i % 5 == 0 else 1 for i in range(60)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    id_names = [i.column for i in report.identifiers]
    assert "user_id" in id_names
    assert "user_id" in report.recommended_drops


def test_11_near_unique_identifier_isolation():
    """Test 11: Near-unique record codes (e.g. 99% unique) are safely isolated."""
    df = pd.DataFrame({
        "record_code": [f"REC_{i}" for i in range(99)] + ["REC_0"],
        "metric": [i % 10 for i in range(100)],
        "target": [0, 1] * 50,
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    assert "record_code" in [i.column for i in report.identifiers]
    assert "record_code" in report.recommended_drops


def test_12_identifier_correlated_with_target():
    """Test 12: An identifier that happens to correlate with target records association in IdentifierIsolation."""
    df = pd.DataFrame({
        "customer_id": range(1, 101),
        "target": [0 if i < 50 else 1 for i in range(100)],
        "legit_feature": [50.0 + (i % 5) for i in range(100)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    id_item = next(i for i in report.identifiers if i.column == "customer_id")
    assert id_item.target_association is not None
    assert id_item.target_association > 0.5


def test_13_no_target_dataset():
    """Test 13: Dataset with no credible target runs target-agnostic checks without crashing."""
    df = pd.DataFrame({
        "entity_id": [f"E_{i}" for i in range(50)],
        "const_col": [42] * 50,
        "feat_a": [i % 5 for i in range(50)],
        "feat_b": [i % 10 for i in range(50)],
    })
    _, columns_meta, _ = generate_fingerprint(df)
    # Empty target candidate list
    report = detect_leakage(df, columns_meta, target_candidates=[])

    assert len(report.identifiers) == 1
    assert "entity_id" in report.recommended_drops
    assert "const_col" in report.recommended_drops
    assert "feat_a" in report.sanitized_feature_columns
    assert "feat_b" in report.sanitized_feature_columns


def test_14_multiple_target_candidates():
    """Test 14: Multiple target candidates are evaluated and findings associate with respective targets."""
    df = pd.DataFrame({
        "churn": [0, 1, 0, 1] * 20,
        "profit": [1000.0 + i * 50 for i in range(80)],
        "churn_copy": [0, 1, 0, 1] * 20,
        "normal_feat": [i % 7 for i in range(80)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    copy_finding = next(f for f in report.findings if f.column == "churn_copy")
    assert copy_finding.target_column == "churn"
    assert copy_finding.risk_level == LeakageRiskLevel.CRITICAL


def test_15_ambiguous_temporal_evidence():
    """Test 15: Temporal features with insufficient timestamp evidence do not raise errors."""
    df = pd.DataFrame({
        "t1": ["2024-01-01", "2024-01-02", np.nan, np.nan],
        "t2": [np.nan, np.nan, "2024-01-03", "2024-01-04"],
        "target": [0, 1, 0, 1],
    })
    fingerprint, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands, temporal=fingerprint.temporal)

    assert isinstance(report, LeakageReport)


def test_16_normal_clean_dataset():
    """Test 16: Clean dataset without leakage has overall_risk == NONE and empty recommended drops (except IDs)."""
    df = pd.DataFrame({
        "age": [20 + (i % 40) for i in range(100)],
        "tenure": [i % 10 for i in range(100)],
        "salary": [30000.0 + i * 500 for i in range(100)],
        "target": [1 if i % 3 == 0 else 0 for i in range(100)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    assert report.has_leakage_risk is False
    assert report.overall_risk == LeakageRiskLevel.NONE
    assert len(report.recommended_drops) == 0
    assert len(report.sanitized_feature_columns) == 3


def test_17_adversarial_false_positive_control():
    """Test 17: Features named 'status' or moderate correlation features are NOT falsely marked as confirmed drop."""
    df = pd.DataFrame({
        "marital_status": ["Single"] * 40 + ["Married"] * 40 + ["Divorced"] * 20,
        "employment_status": ["Employed", "Unemployed"] * 50,
        "target": [1 if i % 3 == 0 else 0 for i in range(100)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    # Status columns that are standard nominal categories should NOT be dropped as post-event
    assert "marital_status" in report.sanitized_feature_columns
    assert "employment_status" in report.sanitized_feature_columns


def test_18_recommendation_correctness():
    """Test 18: Recommendations distinguish exclude_from_model vs review vs use_with_warning."""
    df = pd.DataFrame({
        "id": range(100),
        "target": [0, 1] * 50,
        "exact_copy": [0, 1] * 50,
        "moderate_pred": [0.1 if i % 2 == 0 else 0.9 for i in range(100)],
        "normal_feat": range(100),
    })
    _, columns_meta, target_cands = generate_fingerprint(df)
    report = detect_leakage(df, columns_meta, target_cands)

    copy_f = next(f for f in report.findings if f.column == "exact_copy")
    assert copy_f.recommendation == "exclude_from_model"

    id_f = next(f for f in report.findings if f.column == "id")
    assert id_f.recommendation == "exclude_from_model"


def test_19_leakage_contract_serialization(tmp_path):
    """Test 19: LeakageReport in DiscoveryContract serializes to JSON and deserializes seamlessly."""
    csv_file = tmp_path / "leakage_test.csv"
    df = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(50)],
        "post_event_recovery": [0.0 if i % 4 == 0 else 500.0 for i in range(50)],
        "churn": [1 if i % 4 == 0 else 0 for i in range(50)],
        "age": [30 + i for i in range(50)],
    })
    df.to_csv(csv_file, index=False)

    contract = run_discovery(str(csv_file))

    assert isinstance(contract, DiscoveryContract)
    assert contract.leakage_report.has_leakage_risk is True
    assert "post_event_recovery" in contract.leakage_report.recommended_drops

    # JSON Round-trip
    dumped = contract.model_dump()
    json_str = json.dumps(dumped, default=str)
    reparsed = DiscoveryContract.model_validate(json.loads(json_str))

    assert reparsed.leakage_report.overall_risk == contract.leakage_report.overall_risk
    assert len(reparsed.leakage_report.findings) == len(contract.leakage_report.findings)


def test_20_deterministic_repeated_execution():
    """Test 20: Repeated leakage evaluations on the same dataset produce mathematically identical reports."""
    df = pd.DataFrame({
        "id": range(80),
        "collection_status": ["Paid", "Unpaid", "None", "None"] * 20,
        "default": [1, 1, 0, 0] * 20,
        "score": [500 + i * 5 for i in range(80)],
    })
    _, columns_meta, target_cands = generate_fingerprint(df)

    rep1 = detect_leakage(df, columns_meta, target_cands)
    rep2 = detect_leakage(df, columns_meta, target_cands)

    assert rep1.overall_risk == rep2.overall_risk
    assert rep1.recommended_drops == rep2.recommended_drops
    assert rep1.sanitized_feature_columns == rep2.sanitized_feature_columns
    assert len(rep1.findings) == len(rep2.findings)
