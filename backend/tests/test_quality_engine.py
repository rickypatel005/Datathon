"""
Unit and integration tests for Person 1: Data Quality Engine & Safe Cleaning Audit Engine (Phase 1B).
"""
import pytest
import pandas as pd
import numpy as np
import json
from datetime import datetime

from app.contracts.discovery import (
    QualityReport,
    CleaningAudit,
    ActionRecord,
    TypeMismatch,
    ColumnMetadata,
    InferredDtype,
    DiscoveryContract,
)
from app.pipeline.quality import (
    evaluate_quality,
    analyze_missingness,
    analyze_duplicates,
    analyze_constants_and_near_constants,
    analyze_high_cardinality,
    analyze_numeric_outliers,
    analyze_categorical_quality,
    compute_explainable_quality_score,
    perform_safe_cleaning,
    classify_missingness_severity,
)
from app.pipeline.fingerprint import generate_fingerprint
from app.pipeline.discovery import run_discovery


def test_1_no_quality_issues_dataset():
    """Test 1: Perfectly clean dataset scores 100.0, has 0 warnings, and applies 0 cleaning actions."""
    df = pd.DataFrame({
        "id": [f"ID_{i:04d}" for i in range(100)],
        "age": [20 + (i % 50) for i in range(100)],
        "income": [30000.0 + i * 500.0 for i in range(100)],
        "status": ["Active" if i % 2 == 0 else "Inactive" for i in range(100)],
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert report.overall_quality_score == 100.0
    assert report.duplicate_row_count == 0
    assert report.total_missing_cells == 0
    assert report.total_outliers == 0
    assert len(report.type_mismatches) == 0
    assert len(report.passed_checks) > 0
    assert report.score_breakdown["overall_score"] == 100.0
    assert report.score_breakdown["completeness"] == 100.0
    assert report.score_breakdown["uniqueness"] == 100.0
    assert report.score_breakdown["validity"] == 100.0
    assert report.score_breakdown["structural"] == 100.0
    assert report.score_breakdown["outliers"] == 100.0

    assert len(audit.applied_actions) == 0
    assert audit.original_shape == [100, 4]
    assert audit.cleaned_shape == [100, 4]
    pd.testing.assert_frame_equal(df, cleaned_df)


def test_2_missing_values_classification():
    """Test 2: Missingness thresholds correctly categorize none, low, moderate, high, extreme."""
    assert classify_missingness_severity(0.0) == "none"
    assert classify_missingness_severity(3.5) == "low"
    assert classify_missingness_severity(12.0) == "moderate"
    assert classify_missingness_severity(35.0) == "high"
    assert classify_missingness_severity(75.0) == "extreme"

    # Create dataset with various missingness levels
    n = 100
    df = pd.DataFrame({
        "none_missing": [1.0] * n,
        "low_missing": [1.0] * 97 + [np.nan] * 3,          # 3%
        "mod_missing": [1.0] * 85 + [np.nan] * 15,         # 15%
        "high_missing": [1.0] * 65 + [np.nan] * 35,        # 35%
        "extreme_missing": [1.0] * 20 + [np.nan] * 80,     # 80%
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert report.column_missingness["none_missing"]["severity"] == "none"
    assert report.column_missingness["low_missing"]["severity"] == "low"
    assert report.column_missingness["mod_missing"]["severity"] == "moderate"
    assert report.column_missingness["high_missing"]["severity"] == "high"
    assert report.column_missingness["extreme_missing"]["severity"] == "extreme"
    assert report.total_missing_cells == 3 + 15 + 35 + 80
    assert "extreme_missing" in report.columns_with_missing


def test_3_all_null_column():
    """Test 3: All-null column is detected as 100% missing, penalized, and dropped during safe cleaning."""
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "all_null": [np.nan] * 10,
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert "all_null" in report.columns_with_missing
    assert report.column_missingness["all_null"]["missing_count"] == 10
    assert report.column_missingness["all_null"]["missing_percentage"] == 100.0
    assert "all_null" in audit.dropped_columns
    assert "all_null" not in cleaned_df.columns
    assert cleaned_df.shape == (10, 1)

    # Check drop_column action record
    drop_actions = [a for a in audit.applied_actions if a.action_type == "drop_column"]
    assert len(drop_actions) == 1
    assert drop_actions[0].column == "all_null"
    assert drop_actions[0].affected_rows == 10


def test_4_duplicate_rows_detection_and_cleaning():
    """Test 4: Exact duplicate rows are detected, quantified, and removed in safe cleaning."""
    df = pd.DataFrame({
        "feature1": [1, 2, 2, 3, 4, 4, 4],
        "feature2": ["A", "B", "B", "C", "D", "D", "D"],
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    # In df: row indices 2 is dup of 1; row 5,6 are dups of 4 -> 3 duplicate rows
    assert report.duplicate_row_count == 3
    assert report.unique_row_count == 4
    assert report.duplicate_row_percentage == round((3 / 7) * 100, 2)
    assert len(cleaned_df) == 4

    dup_actions = [a for a in audit.applied_actions if a.action_type == "drop_duplicates"]
    assert len(dup_actions) == 1
    assert dup_actions[0].affected_rows == 3
    assert dup_actions[0].reason == "exact_duplicate_rows"


def test_5_constant_column():
    """Test 5: Constant columns (zero variance) are detected and reported."""
    df = pd.DataFrame({
        "var_col": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "constant_num": [42] * 10,
        "constant_str": ["Fixed"] * 10,
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    const_cols = [c["column"] for c in report.constant_columns]
    assert "constant_num" in const_cols
    assert "constant_str" in const_cols
    assert "var_col" not in const_cols

    const_meta = next(c for c in report.constant_columns if c["column"] == "constant_num")
    assert const_meta["dominant_value"] == 42
    assert const_meta["dominant_ratio"] == 1.0
    assert const_meta["severity"] == "high"


def test_6_near_constant_column():
    """Test 6: Near-constant columns (>95% dominant value) are flagged."""
    df = pd.DataFrame({
        "near_const": ["Normal"] * 96 + ["Rare"] * 4,
        "balanced": ["A"] * 50 + ["B"] * 50,
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    near_cols = [c["column"] for c in report.near_constant_columns]
    assert "near_const" in near_cols
    assert "balanced" not in near_cols

    meta = next(c for c in report.near_constant_columns if c["column"] == "near_const")
    assert meta["dominant_value"] == "Normal"
    assert meta["dominant_frequency"] == 96
    assert meta["dominant_ratio"] == 0.96
    assert meta["severity"] == "moderate"


def test_7_high_cardinality_category():
    """Test 7: Unusually high-cardinality nominal categories are flagged, while genuine IDs/text are not false-flagged."""
    # 100 rows with 60 unique categorical categories (cardinality ratio 0.6)
    df = pd.DataFrame({
        "id_col": [f"ID_{i}" for i in range(100)],
        "high_card_cat": [f"Category_{i % 60}" for i in range(100)],
        "normal_cat": ["A", "B", "C", "D"] * 25,
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    flagged_cols = [c["column"] for c in report.high_cardinality_issues]
    assert "high_card_cat" in flagged_cols
    assert "normal_cat" not in flagged_cols
    assert "id_col" not in flagged_cols  # Identifier should NOT be flagged as high-cardinality categorical


def test_8_numeric_outliers_iqr():
    """Test 8: Generic IQR outlier detection DETECTS and REPORTS outliers deterministically without deleting rows."""
    # Data with median ~ 50, IQR ~ 10, plus extreme values 500 and -200
    normal_data = [45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0, 56.0, 57.0]
    outliers = [500.0, -200.0]
    df = pd.DataFrame({"values": normal_data + outliers})

    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert "values" in report.columns_with_outliers
    assert report.total_outliers == 2
    assert "values" in report.outlier_details

    details = report.outlier_details["values"]
    assert details["outlier_count"] == 2
    assert details["max_outlier"] == 500.0
    assert details["min_outlier"] == -200.0
    assert details["lower_bound"] <= 45
    assert details["upper_bound"] >= 55

    # Default behavior: DETECT + REPORT, do NOT delete rows blindly
    assert len(cleaned_df) == len(df)


def test_9_categorical_rare_values():
    """Test 9: Categorical rare categories are detected in large enough categorical samples."""
    df = pd.DataFrame({
        "region": ["North"] * 50 + ["South"] * 40 + ["Rare1"] * 1 + ["Rare2"] * 1,
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    # Check that warnings contain mention of rare categories
    assert any("rare categories" in w.lower() for w in report.warnings)


def test_10_whitespace_and_casing_inconsistencies():
    """Test 10: Inconsistent whitespace and casing collisions (e.g. 'India', ' India', 'india') are detected."""
    df = pd.DataFrame({
        "country": ["India", " India", "india", "USA", "USA", " USA ", "Germany"] * 10,
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert len(report.categorical_inconsistencies) >= 2
    norm_values = [item["normalized_value"] for item in report.categorical_inconsistencies]
    assert "india" in norm_values
    assert "usa" in norm_values

    # In safe cleaning, whitespace trimming is applied
    trim_actions = [a for a in audit.applied_actions if a.action_type == "trim_whitespace"]
    assert len(trim_actions) >= 1
    assert trim_actions[0].column == "country"
    # In cleaned_df, leading/trailing spaces are removed
    assert not any(val.startswith(" ") or val.endswith(" ") for val in cleaned_df["country"].dropna())


def test_11_mixed_and_invalid_values():
    """Test 11: Mixed numeric and text data in object column is detected as TypeMismatch."""
    df = pd.DataFrame({
        "mixed_col": [10, 20, 30, 40, "Invalid", 50, "N/A_Text", 70, 80, 90],
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert len(report.type_mismatches) == 1
    assert report.type_mismatches[0].column == "mixed_col"
    assert "Mixed" in report.type_mismatches[0].detected_irregularities


def test_12_quality_score_bounds():
    """Test 12: Quality score is strictly bounded between 0.0 and 100.0 across clean, moderate, and terrible datasets."""
    # 1. Clean dataset -> 100.0
    clean_df = pd.DataFrame({"x": range(50), "y": [f"val_{i%5}" for i in range(50)]})
    rep_clean, _, _ = evaluate_quality(clean_df)
    assert 0.0 <= rep_clean.overall_quality_score <= 100.0
    assert rep_clean.overall_quality_score == 100.0

    # 2. Moderate issues -> Between 40.0 and 90.0
    mod_df = pd.DataFrame({
        "x": [1, 2, 2, 3, np.nan, 5, 6, 7, 8, 9],
        "y": ["A", "A", "A", "A", "A", "A", "A", "A", "A", "B"], # near constant
    })
    rep_mod, _, _ = evaluate_quality(mod_df)
    assert 0.0 <= rep_mod.overall_quality_score <= 100.0
    assert rep_mod.overall_quality_score < 100.0

    # 3. Catastrophic dataset -> Bounded at >= 0.0
    bad_df = pd.DataFrame({
        "all_null": [np.nan] * 100,
        "dups": [1] * 100,
        "mixed": ["err"] * 50 + [123] * 50,
    })
    rep_bad, _, _ = evaluate_quality(bad_df)
    assert 0.0 <= rep_bad.overall_quality_score <= 100.0
    assert rep_bad.overall_quality_score < 50.0


def test_13_quality_score_determinism():
    """Test 13: Quality score and breakdown are 100% deterministic across multiple runs."""
    df = pd.DataFrame({
        "num": [10.0, 12.0, np.nan, 14.0, 100.0, 11.0, 12.0],
        "cat": ["A", "B", "A", "B", "B", "B", "B"],
    })
    _, columns_meta, _ = generate_fingerprint(df)

    rep1, _, _ = evaluate_quality(df, columns_meta)
    rep2, _, _ = evaluate_quality(df, columns_meta)

    assert rep1.overall_quality_score == rep2.overall_quality_score
    assert rep1.score_breakdown == rep2.score_breakdown
    assert rep1.warnings == rep2.warnings


def test_14_cleaning_action_audit_structure():
    """Test 14: ActionRecord contains all required audit fields (action, column, affected_rows, reason, method, summaries)."""
    df = pd.DataFrame({
        "age": [25, 30, np.nan, 40, 50],
        "city": ["New York", "London", np.nan, "Paris", "Tokyo"],
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    assert len(audit.applied_actions) >= 2
    for action in audit.applied_actions:
        assert isinstance(action, ActionRecord)
        assert action.action is not None
        assert action.action_type is not None
        assert action.affected_rows > 0
        assert action.reason is not None
        assert action.method is not None
        assert action.before_summary is not None
        assert action.after_summary is not None
        assert isinstance(action.timestamp, str)


def test_15_duplicate_removal_audit():
    """Test 15: Duplicate removal specifically produces an auditable ActionRecord with before and after row counts."""
    df = pd.DataFrame({"a": [1, 1, 2, 3, 3], "b": ["x", "x", "y", "z", "z"]})
    report, audit, cleaned_df = evaluate_quality(df)

    dup_action = next(a for a in audit.applied_actions if a.action_type == "drop_duplicates")
    assert dup_action.affected_rows == 2
    assert dup_action.before_summary["total_rows"] == 5
    assert dup_action.after_summary["total_rows"] == 3
    assert dup_action.method == "drop_duplicates"


def test_16_missing_value_cleaning_audit():
    """Test 16: Safe missing value imputation produces structured ActionRecords for median and mode."""
    df = pd.DataFrame({
        "num_col": [10.0, 20.0, np.nan, 40.0],
        "cat_col": ["Apple", "Banana", np.nan, "Apple"],
    })
    _, columns_meta, _ = generate_fingerprint(df)
    report, audit, cleaned_df = evaluate_quality(df, columns_meta)

    num_action = next(a for a in audit.applied_actions if a.column == "num_col" and a.action_type == "impute_missing")
    assert num_action.method == "median"
    assert num_action.affected_rows == 1
    assert num_action.after_summary["imputed_value"] == 20.0

    cat_action = next(a for a in audit.applied_actions if a.column == "cat_col" and a.action_type == "impute_missing")
    assert cat_action.method == "mode"
    assert cat_action.affected_rows == 1
    assert cat_action.after_summary["imputed_value"] == "Apple"


def test_17_raw_data_remains_unchanged():
    """Test 17: evaluate_quality never mutates the original raw input DataFrame."""
    raw_df = pd.DataFrame({
        "col1": [1, 1, 2, np.nan],
        "col2": [" A ", " B", "   ", "D"],
    })
    raw_df_copy = raw_df.copy(deep=True)

    report, audit, cleaned_df = evaluate_quality(raw_df)

    # raw_df must be byte-for-byte unchanged
    pd.testing.assert_frame_equal(raw_df, raw_df_copy)
    # cleaned_df must have changes applied
    assert not cleaned_df.equals(raw_df)


def test_18_empty_dataset():
    """Test 18: Empty datasets (0 rows or 0 cols) return a valid zero score and empty audit without crashing."""
    df_empty_rows = pd.DataFrame(columns=["a", "b", "c"])
    report, audit, cleaned_df = evaluate_quality(df_empty_rows)

    assert report.overall_quality_score == 0.0
    assert audit.original_shape == [0, 3]
    assert audit.cleaned_shape == [0, 3]
    assert len(audit.applied_actions) == 0

    df_empty_all = pd.DataFrame()
    report2, audit2, cleaned_df2 = evaluate_quality(df_empty_all)
    assert report2.overall_quality_score == 0.0


def test_19_one_row_dataset():
    """Test 19: 1-row datasets are processed safely without statistical divide-by-zero or quantile crashes."""
    df_single = pd.DataFrame({
        "id": ["ID_001"],
        "num": [42.0],
        "cat": ["OnlyOne"],
    })
    _, columns_meta, _ = generate_fingerprint(df_single)
    report, audit, cleaned_df = evaluate_quality(df_single, columns_meta)

    assert 0.0 <= report.overall_quality_score <= 100.0
    assert report.total_outliers == 0
    assert audit.original_shape == [1, 3]
    assert audit.cleaned_shape == [1, 3]


def test_20_tiny_dataset():
    """Test 20: Tiny datasets (2-3 rows) work reliably without exceptions."""
    df_tiny = pd.DataFrame({
        "x": [10.0, np.nan, 30.0],
        "y": ["A", "B", "A"],
    })
    _, columns_meta, _ = generate_fingerprint(df_tiny)
    report, audit, cleaned_df = evaluate_quality(df_tiny, columns_meta)

    assert 0.0 <= report.overall_quality_score <= 100.0
    assert "x" in report.columns_with_missing
    assert len(cleaned_df) == 3


def test_21_id_heavy_dataset():
    """Test 21: Identifier columns with duplicate keys are flagged as quality risks."""
    df_id = pd.DataFrame({
        "user_id": ["USR_1", "USR_2", "USR_1", "USR_3", "USR_4"], # USR_1 duplicated
        "score": [80, 85, 90, 95, 100],
    })
    _, columns_meta, _ = generate_fingerprint(df_id)
    report, audit, cleaned_df = evaluate_quality(df_id, columns_meta)

    # Identifiers shouldn't trigger high cardinality categorical warnings
    assert len(report.high_cardinality_issues) == 0
    # Duplicate identifier entries should be in warnings
    assert any("violating entity uniqueness" in w for w in report.warnings)


def test_22_datetime_dataset():
    """Test 22: Datetime columns are handled properly without erroneous IQR outlier flagging."""
    df_dates = pd.DataFrame({
        "date_col": pd.date_range("2024-01-01", periods=50, freq="D"),
        "sales": [100.0 + i * 2 for i in range(50)],
    })
    _, columns_meta, _ = generate_fingerprint(df_dates)
    report, audit, cleaned_df = evaluate_quality(df_dates, columns_meta)

    assert "date_col" not in report.columns_with_outliers
    assert report.overall_quality_score == 100.0


def test_23_currency_and_percentage_dataset():
    """Test 23: Currency, percentage, and postal codes from Phase 1A are cleanly processed."""
    df_special = pd.DataFrame({
        "price": ["$10.50", "$25.00", "$15.75", "$30.00", "$20.00"] * 10,
        "discount": ["5%", "10%", "15%", "0%", "20%"] * 10,
        "zip": ["90210", "94105", "10001", "30301", "60601"] * 10,
    })
    _, columns_meta, _ = generate_fingerprint(df_special)
    report, audit, cleaned_df = evaluate_quality(df_special, columns_meta)

    assert 0.0 <= report.overall_quality_score <= 100.0
    assert report.total_missing_cells == 0


def test_24_discovery_contract_validation_and_json_serializable(tmp_path):
    """Test 24: Full end-to-end discovery run produces fully valid JSON-serializable DiscoveryContract."""
    csv_file = tmp_path / "test_discovery.csv"
    df = pd.DataFrame({
        "user_id": [f"U{i:04d}" for i in range(60)],
        "age": [20 + (i % 40) if i != 5 else np.nan for i in range(60)],
        "salary": [50000.0 + i * 1000.0 for i in range(60)],
        "churn": [1 if i % 4 == 0 else 0 for i in range(60)],
        "country": ["USA", " Canada", "USA", "UK"] * 15,
    })
    df.to_csv(csv_file, index=False)

    contract = run_discovery(str(csv_file))

    assert isinstance(contract, DiscoveryContract)
    assert contract.version == "1.0.0"
    assert contract.quality_report.overall_quality_score > 0
    assert len(contract.cleaning_audit.applied_actions) > 0

    # Ensure JSON serializability
    contract_dict = contract.model_dump()
    json_str = json.dumps(contract_dict, default=str)
    assert len(json_str) > 0

    # Round-trip verification
    reparsed = DiscoveryContract.model_validate(json.loads(json_str))
    assert reparsed.dataset_name == "test_discovery.csv"
    assert reparsed.quality_report.overall_quality_score == contract.quality_report.overall_quality_score
