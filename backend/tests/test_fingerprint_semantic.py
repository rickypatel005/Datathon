"""
Comprehensive unit tests for Phase 1A: Deep Semantic Type Inference & Dataset Fingerprinting.
Tests 22 distinct semantic cases and misleading edge cases.
"""
import pytest
import pandas as pd
import numpy as np

from app.contracts.discovery import (
    InferredDtype,
    TaskType,
    DiscoveryContract,
)
from app.pipeline.fingerprint import (
    infer_column_semantics,
    generate_fingerprint,
    rank_target_candidates,
    detect_temporal_structure,
    calculate_class_balance,
)


def test_1_continuous_numeric():
    """Verify float values with fractional components are inferred as continuous numeric."""
    s = pd.Series([12.34, 45.67, 89.12, 34.56, 78.90, 23.45, 67.89, 12.01])
    res = infer_column_semantics(s, "temperature_celsius", len(s))
    assert res.inferred_type == InferredDtype.NUMERIC_CONTINUOUS
    assert res.subtype == "continuous_measurement"
    assert "fractional" in res.reasons[0].lower() or "continuous" in res.reasons[0].lower()


def test_2_discrete_numeric():
    """Verify integer counts are inferred as discrete numeric."""
    s = pd.Series([1, 0, 3, 2, 5, 4, 2, 1, 0, 6, 2, 3])
    res = infer_column_semantics(s, "orders_count", len(s))
    assert res.inferred_type == InferredDtype.NUMERIC_DISCRETE
    assert res.subtype == "count_discrete"


def test_3_binary_categorical():
    """Verify 2-class non-boolean nominal strings are inferred as boolean or nominal categorical."""
    s = pd.Series(["Group A", "Group B", "Group A", "Group B", "Group A"])
    res = infer_column_semantics(s, "treatment_arm", len(s))
    assert res.inferred_type in (InferredDtype.CATEGORICAL_NOMINAL, InferredDtype.BOOLEAN)


def test_4_multiclass_categorical():
    """Verify unordered string categories are inferred as nominal categorical."""
    s = pd.Series(["HR", "Engineering", "Marketing", "Sales", "Finance", "Legal"] * 10)
    res = infer_column_semantics(s, "department", len(s))
    assert res.inferred_type == InferredDtype.CATEGORICAL_NOMINAL
    assert res.subtype == "nominal_category"


def test_5_boolean_variations():
    """Verify boolean variations (Yes/No, True/False, 0/1 flags) are recognized as boolean."""
    s1 = pd.Series(["Yes", "No", "Yes", "Yes", "No"])
    res1 = infer_column_semantics(s1, "is_subscriber", len(s1))
    assert res1.inferred_type == InferredDtype.BOOLEAN

    s2 = pd.Series([True, False, True, True, False])
    res2 = infer_column_semantics(s2, "has_discount", len(s2))
    assert res2.inferred_type == InferredDtype.BOOLEAN

    s3 = pd.Series(["active", "inactive", "active"])
    res3 = infer_column_semantics(s3, "account_status", len(s3))
    assert res3.inferred_type == InferredDtype.BOOLEAN


def test_6_datetime_native_dtype():
    """Verify native pandas datetime64 columns are recognized."""
    s = pd.date_range("2025-01-01", periods=10, freq="D")
    res = infer_column_semantics(pd.Series(s), "created_at", len(s))
    assert res.inferred_type == InferredDtype.DATETIME
    assert res.subtype == "native_datetime"


def test_7_date_strings():
    """Verify ISO and calendar date strings are recognized."""
    s = pd.Series(["2025-01-15", "2025-02-20", "2025-03-25", "2025-04-30"])
    res = infer_column_semantics(s, "transaction_date", len(s))
    assert res.inferred_type == InferredDtype.DATETIME


def test_8_free_form_text():
    """Verify long descriptions/comments are inferred as free text."""
    s = pd.Series([
        "The customer called to complain about a delayed delivery and requested a refund immediately.",
        "User experienced difficulties during the checkout process and payment gateway timed out repeatedly.",
        "Excellent support provided by the agent. Everything was resolved within five minutes smoothly.",
    ])
    res = infer_column_semantics(s, "customer_feedback", len(s))
    assert res.inferred_type == InferredDtype.FREE_TEXT
    assert res.subtype == "free_text_comment"


def test_9_near_unique_identifier():
    """Verify near-unique alphanumeric tokens are classified as identifiers."""
    s = pd.Series([f"TOK_{i:05d}" for i in range(100)])
    res = infer_column_semantics(s, "auth_token", len(s))
    assert res.inferred_type == InferredDtype.IDENTIFIER
    assert res.is_identifier is True


def test_10_uuid_identifier():
    """Verify UUID formatted strings are recognized as UUID identifiers."""
    s = pd.Series([
        "c3f380d9-4f4c-4ac8-b2d6-bd46e43b99f6",
        "19a77c1d-a303-4199-9d4a-11c0e30feb98",
        "92747417-497d-4c28-b00e-d189c35a8c12",
        "6fde9bd9-2e81-41f5-b644-52c1880c5c28",
    ])
    res = infer_column_semantics(s, "session_id", len(s))
    assert res.inferred_type == InferredDtype.IDENTIFIER
    assert res.subtype == "uuid"
    assert res.confidence >= 0.95


def test_11_postal_zip_code_not_numeric():
    """CRUCIAL: Verify ZIP codes with leading zeros ('00123') remain postal codes, NOT cast to plain integers."""
    s = pd.Series(["00123", "02138", "90210", "10001", "07030", "94103"])
    res = infer_column_semantics(s, "postal_zip", len(s))
    assert res.subtype == "postal_code"
    assert res.is_identifier is True
    # Must not be continuous numeric!
    assert res.inferred_type in (InferredDtype.IDENTIFIER, InferredDtype.CATEGORICAL_NOMINAL)


def test_12_currency_strings():
    """Verify currency formatted strings ($1,200.50, ₹50,000) are recognized and parsed."""
    s = pd.Series(["₹50,000", "₹120,500", "₹35,200", "₹80,000", "₹95,000"])
    res = infer_column_semantics(s, "base_salary", len(s))
    assert res.inferred_type == InferredDtype.NUMERIC_CONTINUOUS
    assert res.subtype == "currency"
    assert res.parsed_numeric_series is not None
    assert res.parsed_numeric_series.iloc[0] == 50000.0


def test_13_percentage_strings():
    """Verify percentage strings ('75%', '12.5%') are recognized and parsed."""
    s = pd.Series(["75%", "12.5%", "99.9%", "45.0%", "5.2%"])
    res = infer_column_semantics(s, "discount_pct", len(s))
    assert res.inferred_type == InferredDtype.NUMERIC_CONTINUOUS
    assert res.subtype == "percentage"
    assert res.parsed_numeric_series is not None
    assert res.parsed_numeric_series.iloc[0] == 75.0


def test_14_ordinal_scale_values():
    """Verify recognized ordered categories (low/medium/high, poor/fair/good) are inferred as ordinal."""
    s = pd.Series(["Low", "Medium", "High", "Critical", "Medium", "Low", "High"] * 5)
    res = infer_column_semantics(s, "ticket_priority", len(s))
    assert res.inferred_type == InferredDtype.CATEGORICAL_ORDINAL
    assert res.subtype == "ordinal_scale"


def test_15_mixed_type_handling():
    """Verify mixed-type columns with nulls and strings degrade safely without raising exceptions."""
    s = pd.Series([12, "Unknown", np.nan, 45, "None", 88, np.nan])
    res = infer_column_semantics(s, "mixed_data", len(s))
    assert res.inferred_type is not None
    assert res.confidence > 0.0


def test_16_missing_heavy_column():
    """Verify columns with mostly missing values are recognized and penalized for target consideration."""
    s = pd.Series([np.nan] * 90 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    df = pd.DataFrame({"sparse_col": s, "feature": range(100)})
    fingerprint, cols, targets = generate_fingerprint(df)
    target_names = [t.column_name for t in targets]
    assert "sparse_col" not in target_names


def test_17_high_cardinality_categorical():
    """Verify high cardinality categoricals are indexed in fingerprint."""
    df = pd.DataFrame({
        "city_name": [f"City_{i}" for i in range(40)] * 2,
        "amount": np.random.uniform(10, 100, 80),
    })
    fingerprint, cols, targets = generate_fingerprint(df)
    assert "city_name" in fingerprint.categorical_columns or "city_name" in fingerprint.text_columns


def test_18_classification_target_ranking():
    """Verify binary churn target candidate is prioritized with high confidence score."""
    df = pd.DataFrame({
        "customer_id": [f"ID_{i}" for i in range(100)],
        "age": np.random.randint(20, 60, 100),
        "balance": np.random.uniform(100, 5000, 100),
        "churn": np.random.choice([0, 1], 100, p=[0.8, 0.2]),
    })
    targets = rank_target_candidates(df, generate_fingerprint(df)[1], len(df))
    assert len(targets) >= 1
    assert targets[0].column_name == "churn"
    assert targets[0].task_type == TaskType.BINARY_CLASSIFICATION
    assert targets[0].confidence_score >= 0.90


def test_19_regression_target_ranking():
    """Verify continuous price target candidate is identified for regression."""
    df = pd.DataFrame({
        "house_id": [f"H_{i}" for i in range(100)],
        "sqft": np.random.randint(500, 3000, 100),
        "bedrooms": np.random.randint(1, 5, 100),
        "price": np.random.uniform(100000, 800000, 100),
    })
    targets = rank_target_candidates(df, generate_fingerprint(df)[1], len(df))
    assert len(targets) >= 1
    assert targets[0].column_name == "price"
    assert targets[0].task_type == TaskType.REGRESSION
    assert targets[0].confidence_score >= 0.80


def test_20_no_obvious_target_unsupervised():
    """Verify dataset with no clear target routes to clustering / unsupervised."""
    df = pd.DataFrame({
        "dim_1": np.random.uniform(0, 1, 50),
        "dim_2": np.random.uniform(0, 1, 50),
        "dim_3": np.random.uniform(0, 1, 50),
    })
    fingerprint, cols, targets = generate_fingerprint(df)
    assert TaskType.CLUSTERING in fingerprint.task_type_candidates


def test_21_temporal_structure_detection():
    """Verify time series ordering and frequency inference."""
    dates = pd.date_range("2025-01-01", periods=30, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "value": np.random.uniform(10, 50, 30),
    })
    temporal = detect_temporal_structure(df, ["timestamp"])
    assert temporal is not None
    assert temporal.is_sorted is True
    assert temporal.distinct_dates_count == 30
    assert temporal.start_date.startswith("2025-01-01")


def test_22_non_temporal_dataset():
    """Verify non-temporal dataset returns None for temporal structure."""
    df = pd.DataFrame({
        "feat_a": [1, 2, 3, 4],
        "feat_b": [5, 6, 7, 8],
    })
    temporal = detect_temporal_structure(df, [])
    assert temporal is None


def test_23_class_balance_calculation():
    """Verify minority class and imbalance ratio calculation."""
    df = pd.DataFrame({
        "target": ["No"] * 85 + ["Yes"] * 15
    })
    balance = calculate_class_balance(df, "target")
    assert balance is not None
    assert balance.minority_class == "Yes"
    assert balance.minority_class_percentage == 15.0
    assert balance.is_imbalanced is True
    assert balance.imbalance_ratio == pytest.approx(5.67, rel=1e-2)
