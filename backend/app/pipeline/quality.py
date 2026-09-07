"""
Person 1: Data Quality Engine & Safe Cleaning Audit Engine.
Evaluates dataset health, missingness patterns, duplicates, constant/near-constant columns,
high cardinality, numerical outliers, categorical anomalies, whitespace inconsistencies,
and type mismatches. Generates explainable bounded quality scores and an immutable cleaning audit trail.
"""
from typing import Tuple, List, Dict, Any, Optional, Set
import re
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from app.contracts.discovery import (
    QualityReport,
    CleaningAudit,
    ActionRecord,
    TypeMismatch,
    ColumnMetadata,
    InferredDtype,
)


# ─── Centralized Configurable Quality Thresholds ────────────────────

# Missingness Thresholds (%)
MISSING_NONE_MAX = 0.0
MISSING_LOW_MAX = 5.0
MISSING_MODERATE_MAX = 20.0
MISSING_HIGH_MAX = 50.0
# Above 50.0% is classified as "extreme"

# Cleaning Thresholds
DROP_COLUMN_MISSING_THRESHOLD = 70.0  # Drop columns if missing > 70%
SAFE_IMPUTATION_MAX_MISSING = 50.0    # Impute missing values if missing <= 50%

# Constant & Near-Constant Thresholds
CONSTANT_RATIO_THRESHOLD = 1.0
NEAR_CONSTANT_RATIO_THRESHOLD = 0.95
NEAR_CONSTANT_MIN_ROWS = 10

# High Cardinality Thresholds (for categorical nominal/ordinal)
HIGH_CARDINALITY_RATIO_THRESHOLD = 0.5
HIGH_CARDINALITY_MIN_UNIQUE = 20
HIGH_CARDINALITY_ABSOLUTE_UNIQUE = 50

# Rare Category Thresholds
RARE_CATEGORY_MAX_FREQ = 2
RARE_CATEGORY_MAX_RATIO = 0.01
RARE_CATEGORY_MIN_ROWS = 50

# Outlier Detection Thresholds (IQR)
OUTLIER_IQR_MULTIPLIER = 1.5
OUTLIER_MIN_ROWS = 5


def classify_missingness_severity(missing_pct: float) -> str:
    """Classify missing percentage into standardized severity tiers."""
    if missing_pct <= MISSING_NONE_MAX:
        return "none"
    elif missing_pct <= MISSING_LOW_MAX:
        return "low"
    elif missing_pct <= MISSING_MODERATE_MAX:
        return "moderate"
    elif missing_pct <= MISSING_HIGH_MAX:
        return "high"
    else:
        return "extreme"


# ─── Sub-Analysis 1: Missingness ───────────────────────────────────

def analyze_missingness(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Dict[str, Any]:
    """
    Perform deep missingness analysis per column and dataset-wide.
    Correctly accounts for standard NaN/None as well as empty and whitespace-only strings.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    columns_with_missing: List[str] = []
    column_missingness: Dict[str, Dict[str, Any]] = {}
    all_null_columns: List[str] = []
    total_missing_cells = 0
    warnings: List[str] = []
    passed_checks: List[str] = []

    if total_rows == 0 or total_cols == 0:
        return {
            "total_missing_cells": 0,
            "missing_cell_percentage": 0.0,
            "columns_with_missing": [],
            "column_missingness": {},
            "all_null_columns": [],
            "warnings": ["Dataset has 0 rows or 0 columns."],
            "passed_checks": [],
        }

    for col in df.columns:
        series = df[col]
        # Detect standard nulls
        null_mask = series.isnull()
        
        # Detect whitespace-only or empty strings in object/string columns
        whitespace_count = 0
        if series.dtype == object or pd.api.types.is_string_dtype(series):
            # Inspect non-null string entries
            non_null_s = series.dropna()
            str_converted = non_null_s.astype(str)
            whitespace_mask = str_converted.str.strip().eq("")
            whitespace_count = int(whitespace_mask.sum())

        effective_missing = int(null_mask.sum()) + whitespace_count
        effective_missing = min(effective_missing, total_rows)
        non_missing = total_rows - effective_missing
        missing_pct = round((effective_missing / total_rows) * 100, 2)
        missing_ratio = round(effective_missing / total_rows, 4)
        severity = classify_missingness_severity(missing_pct)

        column_missingness[col] = {
            "missing_count": effective_missing,
            "missing_ratio": missing_ratio,
            "missing_percentage": missing_pct,
            "non_missing_count": non_missing,
            "severity": severity,
            "whitespace_missing_count": whitespace_count,
        }

        total_missing_cells += effective_missing

        if effective_missing > 0:
            columns_with_missing.append(col)
            if effective_missing == total_rows:
                all_null_columns.append(col)
                warnings.append(f"Column '{col}' is entirely null (100% missing values).")
            elif severity in ("high", "extreme"):
                warnings.append(
                    f"Column '{col}' has {severity} missingness: {effective_missing}/{total_rows} ({missing_pct}%)."
                )

        if whitespace_count > 0:
            warnings.append(
                f"Column '{col}' contains {whitespace_count} empty or whitespace-only strings that represent missing values."
            )

    missing_cell_pct = round((total_missing_cells / max(total_cells, 1)) * 100, 2)

    if total_missing_cells == 0:
        passed_checks.append("Zero missing values across all columns.")
    else:
        warnings.insert(
            0,
            f"Detected {total_missing_cells} missing cells ({missing_cell_pct}% of total cells) across {len(columns_with_missing)} columns."
        )

    return {
        "total_missing_cells": total_missing_cells,
        "missing_cell_percentage": missing_cell_pct,
        "columns_with_missing": columns_with_missing,
        "column_missingness": column_missingness,
        "all_null_columns": all_null_columns,
        "warnings": warnings,
        "passed_checks": passed_checks,
    }


# ─── Sub-Analysis 2: Duplicates ────────────────────────────────────

def analyze_duplicates(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Dict[str, Any]:
    """
    Analyze exact duplicate rows and semantic identifier duplicates.
    """
    total_rows = len(df)
    warnings: List[str] = []
    passed_checks: List[str] = []
    identifier_duplicates: List[Dict[str, Any]] = []

    if total_rows == 0:
        return {
            "duplicate_row_count": 0,
            "duplicate_row_percentage": 0.0,
            "unique_row_count": 0,
            "identifier_duplicates": [],
            "warnings": [],
            "passed_checks": [],
        }

    # 1. Exact Duplicate Rows
    dup_row_count = int(df.duplicated().sum())
    unique_row_count = total_rows - dup_row_count
    dup_row_pct = round((dup_row_count / total_rows) * 100, 2)

    if dup_row_count > 0:
        warnings.append(f"Detected {dup_row_count} ({dup_row_pct}%) exact duplicate rows.")
    else:
        passed_checks.append("Zero duplicate rows detected.")

    # 2. Identifier Duplicate Analysis
    for col_name, meta in columns_meta_dict.items():
        if col_name in df.columns and (meta.is_identifier or meta.inferred_type == InferredDtype.IDENTIFIER):
            s = df[col_name].dropna()
            if len(s) > 0:
                id_dups = int(s.duplicated().sum())
                if id_dups > 0:
                    id_dup_ratio = round(id_dups / len(s), 4)
                    identifier_duplicates.append({
                        "column": col_name,
                        "duplicate_count": id_dups,
                        "duplicate_ratio": id_dup_ratio,
                        "reason": f"Semantic entity key '{col_name}' contains {id_dups} duplicate keys.",
                    })
                    warnings.append(
                        f"Primary/declared identifier '{col_name}' contains {id_dups} ({round(id_dup_ratio*100, 2)}%) duplicate entries, violating entity uniqueness."
                    )

    return {
        "duplicate_row_count": dup_row_count,
        "duplicate_row_percentage": dup_row_pct,
        "unique_row_count": unique_row_count,
        "identifier_duplicates": identifier_duplicates,
        "warnings": warnings,
        "passed_checks": passed_checks,
    }


# ─── Sub-Analysis 3: Constant & Near-Constant Columns ───────────────

def analyze_constants_and_near_constants(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Dict[str, Any]:
    """
    Detect constant (zero variance) and near-constant (> 95% dominant) columns.
    """
    constant_columns: List[Dict[str, Any]] = []
    near_constant_columns: List[Dict[str, Any]] = []
    warnings: List[str] = []
    passed_checks: List[str] = []

    total_rows = len(df)
    if total_rows == 0:
        return {
            "constant_columns": [],
            "near_constant_columns": [],
            "warnings": [],
            "passed_checks": [],
        }

    for col in df.columns:
        s = df[col].dropna()
        non_null_count = len(s)
        if non_null_count == 0:
            continue  # Handled as all-null in missingness

        unique_count = s.nunique()
        if unique_count == 1:
            dominant_val = s.iloc[0]
            if isinstance(dominant_val, (np.generic, pd.Timestamp)):
                dominant_val = dominant_val.item() if hasattr(dominant_val, "item") else str(dominant_val)

            constant_columns.append({
                "column": col,
                "dominant_value": dominant_val,
                "dominant_frequency": non_null_count,
                "dominant_ratio": 1.0,
                "severity": "high",
                "explanation": f"Column '{col}' has zero variance: 100% of non-null entries equal '{dominant_val}'.",
            })
            warnings.append(f"Column '{col}' is constant (zero variance with single value '{dominant_val}').")
        elif unique_count > 1 and non_null_count >= NEAR_CONSTANT_MIN_ROWS:
            top_val = s.value_counts().index[0]
            top_freq = int(s.value_counts().iloc[0])
            top_ratio = round(top_freq / non_null_count, 4)

            if top_ratio >= NEAR_CONSTANT_RATIO_THRESHOLD:
                if isinstance(top_val, (np.generic, pd.Timestamp)):
                    top_val = top_val.item() if hasattr(top_val, "item") else str(top_val)

                near_constant_columns.append({
                    "column": col,
                    "dominant_value": top_val,
                    "dominant_frequency": top_freq,
                    "dominant_ratio": top_ratio,
                    "severity": "moderate",
                    "explanation": f"Column '{col}' is near-constant: dominant value '{top_val}' accounts for {round(top_ratio * 100, 1)}% of rows.",
                })
                warnings.append(
                    f"Column '{col}' is near-constant: dominant value '{top_val}' appears in {round(top_ratio * 100, 1)}% of rows."
                )

    if not constant_columns and not near_constant_columns:
        passed_checks.append("No constant or near-constant uninformative columns detected.")

    return {
        "constant_columns": constant_columns,
        "near_constant_columns": near_constant_columns,
        "warnings": warnings,
        "passed_checks": passed_checks,
    }


# ─── Sub-Analysis 4: High Cardinality ──────────────────────────────

def analyze_high_cardinality(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Dict[str, Any]:
    """
    Detect abnormally high cardinality in categorical features.
    Carefully ignores identifiers, free text, and dates to avoid false positives.
    """
    high_cardinality_issues: List[Dict[str, Any]] = []
    warnings: List[str] = []
    total_rows = len(df)

    if total_rows < 10:
        return {"high_cardinality_issues": [], "warnings": []}

    for col in df.columns:
        meta = columns_meta_dict.get(col)
        # Only evaluate nominal/ordinal categorical columns
        if meta and meta.inferred_type in (
            InferredDtype.IDENTIFIER,
            InferredDtype.TEXT,
            InferredDtype.FREE_TEXT,
            InferredDtype.DATETIME,
        ):
            continue

        if meta and meta.is_identifier:
            continue

        s = df[col].dropna()
        if len(s) == 0:
            continue

        unique_count = s.nunique()
        card_ratio = round(unique_count / len(s), 4)

        # Flag if cardinality ratio is high or unique count is very large for a categorical column
        if meta and meta.inferred_type in (InferredDtype.CATEGORICAL_NOMINAL, InferredDtype.CATEGORICAL_ORDINAL):
            if (unique_count > HIGH_CARDINALITY_ABSOLUTE_UNIQUE and card_ratio > 0.2) or (
                unique_count >= HIGH_CARDINALITY_MIN_UNIQUE and card_ratio > HIGH_CARDINALITY_RATIO_THRESHOLD
            ):
                severity = "high" if card_ratio > 0.7 else "moderate"
                reason = f"Categorical feature '{col}' has high cardinality ({unique_count} distinct categories, {round(card_ratio*100, 1)}% unique ratio)."
                high_cardinality_issues.append({
                    "column": col,
                    "unique_count": unique_count,
                    "unique_ratio": card_ratio,
                    "severity": severity,
                    "reason": reason,
                })
                warnings.append(reason)

    return {
        "high_cardinality_issues": high_cardinality_issues,
        "warnings": warnings,
    }


# ─── Sub-Analysis 5: Numerical Outliers ────────────────────────────

def analyze_numeric_outliers(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Dict[str, Any]:
    """
    Detect numerical outliers deterministically using the IQR method.
    Default behavior is DETECT + REPORT.
    """
    total_outliers = 0
    columns_with_outliers: List[str] = []
    outlier_details: Dict[str, Dict[str, Any]] = {}
    warnings: List[str] = []
    passed_checks: List[str] = []

    for col in df.columns:
        meta = columns_meta_dict.get(col)
        # Only evaluate numeric continuous/discrete columns (skip booleans and identifiers)
        if meta and meta.inferred_type in (InferredDtype.BOOLEAN, InferredDtype.IDENTIFIER):
            continue

        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        s = df[col].dropna()
        if len(s) < OUTLIER_MIN_ROWS:
            continue

        q25 = float(s.quantile(0.25))
        q75 = float(s.quantile(0.75))
        iqr = q75 - q25

        if iqr > 0:
            lower_bound = q25 - OUTLIER_IQR_MULTIPLIER * iqr
            upper_bound = q75 + OUTLIER_IQR_MULTIPLIER * iqr

            outliers_mask = (s < lower_bound) | (s > upper_bound)
            outliers_count = int(outliers_mask.sum())

            if outliers_count > 0:
                total_outliers += outliers_count
                columns_with_outliers.append(col)
                outlier_pct = round((outliers_count / len(s)) * 100, 2)

                low_outliers = s[s < lower_bound]
                high_outliers = s[s > upper_bound]

                outlier_details[col] = {
                    "q1": round(q25, 4),
                    "q3": round(q75, 4),
                    "iqr": round(iqr, 4),
                    "lower_bound": round(lower_bound, 4),
                    "upper_bound": round(upper_bound, 4),
                    "outlier_count": outliers_count,
                    "outlier_percentage": outlier_pct,
                    "min_outlier": round(float(low_outliers.min()), 4) if len(low_outliers) > 0 else None,
                    "max_outlier": round(float(high_outliers.max()), 4) if len(high_outliers) > 0 else None,
                }

                if outlier_pct > 5.0:
                    warnings.append(
                        f"Numeric column '{col}' has {outliers_count} ({outlier_pct}%) IQR outliers outside [{round(lower_bound, 2)}, {round(upper_bound, 2)}]."
                    )

    if total_outliers == 0:
        passed_checks.append("Zero numerical outliers detected via IQR.")
    else:
        warnings.insert(
            0,
            f"Detected {total_outliers} numerical outliers across {len(columns_with_outliers)} numeric column(s)."
        )

    return {
        "total_outliers": total_outliers,
        "columns_with_outliers": columns_with_outliers,
        "outlier_details": outlier_details,
        "warnings": warnings,
        "passed_checks": passed_checks,
    }


# ─── Sub-Analysis 6: Categorical Consistency & Mixed Types ──────────

def analyze_categorical_quality(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Dict[str, Any]:
    """
    Detect whitespace/case collisions (e.g. 'India' vs ' India' vs 'india'),
    rare categories, and mixed/incompatible value types.
    """
    categorical_inconsistencies: List[Dict[str, Any]] = []
    type_mismatches: List[TypeMismatch] = []
    warnings: List[str] = []
    passed_checks: List[str] = []

    for col in df.columns:
        s = df[col].dropna()
        if len(s) == 0:
            continue

        # 1. Whitespace and Case Collisions for string columns
        if s.dtype == object or pd.api.types.is_string_dtype(s):
            str_series = s.astype(str)
            raw_counts = str_series.value_counts().to_dict()

            # Group raw strings by stripped lowercase representation
            normalized_groups: Dict[str, List[str]] = {}
            for raw_val in raw_counts.keys():
                norm_key = str(raw_val).strip().lower()
                normalized_groups.setdefault(norm_key, []).append(str(raw_val))

            # Detect collisions
            collisions = {k: v for k, v in normalized_groups.items() if len(v) > 1 and k != ""}
            if collisions:
                for norm_key, variants in collisions.items():
                    affected_count = sum(raw_counts[v] for v in variants)
                    categorical_inconsistencies.append({
                        "column": col,
                        "normalized_value": norm_key,
                        "raw_variants": variants,
                        "variant_counts": {v: raw_counts[v] for v in variants},
                        "total_affected_rows": affected_count,
                        "severity": "moderate" if len(variants) > 2 else "low",
                        "explanation": f"Column '{col}' has {len(variants)} inconsistent casing/whitespace variants of '{norm_key}': {variants}.",
                    })
                    warnings.append(
                        f"Column '{col}' contains inconsistent variations of '{norm_key}': {variants} (total {affected_count} rows)."
                    )

            # 2. Mixed Type Detection in Object Columns
            # Check if column mixes numeric values with arbitrary strings
            numeric_parsed = pd.to_numeric(s, errors="coerce")
            num_numeric = int(numeric_parsed.notnull().sum())
            num_non_numeric = len(s) - num_numeric

            if num_numeric > 0 and num_non_numeric > 0 and len(s) >= 5:
                # If a substantial portion is numeric but some are strings
                if 0.1 <= (num_numeric / len(s)) <= 0.95:
                    type_mismatches.append(TypeMismatch(
                        column=col,
                        declared_type=str(df[col].dtype),
                        detected_irregularities=f"Mixed values: {num_numeric} numeric rows and {num_non_numeric} non-numeric string rows.",
                        count=num_non_numeric,
                    ))
                    warnings.append(
                        f"Column '{col}' contains mixed data types ({num_numeric} numeric, {num_non_numeric} text/string rows)."
                    )

        # 3. Rare Categories in Categorical Features
        meta = columns_meta_dict.get(col)
        if meta and meta.inferred_type in (InferredDtype.CATEGORICAL_NOMINAL, InferredDtype.CATEGORICAL_ORDINAL):
            if len(s) >= RARE_CATEGORY_MIN_ROWS:
                val_counts = s.value_counts()
                rare_mask = (val_counts <= RARE_CATEGORY_MAX_FREQ) | ((val_counts / len(s)) < RARE_CATEGORY_MAX_RATIO)
                rare_cats = val_counts[rare_mask]
                if 0 < len(rare_cats) < len(val_counts):
                    rare_rows = int(rare_cats.sum())
                    rare_pct = round((rare_rows / len(s)) * 100, 2)
                    if rare_pct > 2.0:
                        warnings.append(
                            f"Column '{col}' has {len(rare_cats)} rare categories ({rare_rows} rows, {rare_pct}% of column)."
                        )

    if not categorical_inconsistencies and not type_mismatches:
        passed_checks.append("Zero categorical whitespace/casing inconsistencies or mixed types detected.")

    return {
        "categorical_inconsistencies": categorical_inconsistencies,
        "type_mismatches": type_mismatches,
        "warnings": warnings,
        "passed_checks": passed_checks,
    }


# ─── Quality Score Computation (100-Point Explainable & Bounded) ───

def compute_explainable_quality_score(
    total_rows: int,
    total_cols: int,
    missingness_res: Dict[str, Any],
    duplicate_res: Dict[str, Any],
    constant_res: Dict[str, Any],
    high_card_res: Dict[str, Any],
    outlier_res: Dict[str, Any],
    categorical_res: Dict[str, Any],
) -> Tuple[float, Dict[str, float]]:
    """
    Compute a deterministic, explainable, bounded 100-point data health score.

    Dimensions:
      1. Completeness (Max deduction: 35.0 pts)
      2. Uniqueness (Max deduction: 20.0 pts)
      3. Validity & Consistency (Max deduction: 15.0 pts)
      4. Structural & Variance (Max deduction: 15.0 pts)
      5. Outliers (Max deduction: 15.0 pts)
    """
    if total_rows == 0 or total_cols == 0:
        return 0.0, {
            "completeness": 0.0,
            "uniqueness": 0.0,
            "validity": 0.0,
            "structural": 0.0,
            "outliers": 0.0,
            "overall_score": 0.0,
        }

    # 1. Completeness Deductions
    missing_pct = missingness_res["missing_cell_percentage"]
    all_null_cols_count = len(missingness_res["all_null_columns"])
    
    comp_deduction = min(missing_pct * 1.5, 25.0)
    if all_null_cols_count > 0:
        comp_deduction += min((all_null_cols_count / max(total_cols, 1)) * 10.0, 10.0)
    comp_score = max(0.0, 100.0 - (comp_deduction / 35.0) * 100.0)

    # 2. Uniqueness Deductions
    dup_row_pct = duplicate_res["duplicate_row_percentage"]
    id_dups_count = len(duplicate_res["identifier_duplicates"])
    
    uniq_deduction = min(dup_row_pct * 2.0, 15.0)
    if id_dups_count > 0:
        uniq_deduction += 5.0
    uniq_score = max(0.0, 100.0 - (uniq_deduction / 20.0) * 100.0)

    # 3. Validity & Consistency Deductions
    type_mismatch_count = len(categorical_res["type_mismatches"])
    inconsistency_count = len(categorical_res["categorical_inconsistencies"])
    
    val_deduction = min(type_mismatch_count * 3.0, 10.0) + min(inconsistency_count * 2.0, 5.0)
    val_score = max(0.0, 100.0 - (val_deduction / 15.0) * 100.0)

    # 4. Structural & Variance Deductions
    const_count = len(constant_res["constant_columns"])
    near_const_count = len(constant_res["near_constant_columns"])
    high_card_count = len(high_card_res["high_cardinality_issues"])

    struct_deduction = min(const_count * 5.0, 8.0) + min(near_const_count * 2.0, 4.0) + min(high_card_count * 1.5, 3.0)
    struct_score = max(0.0, 100.0 - (struct_deduction / 15.0) * 100.0)

    # 5. Outlier Deductions
    total_outliers = outlier_res["total_outliers"]
    total_cells = total_rows * total_cols
    outlier_ratio = total_outliers / max(total_cells, 1)
    
    outlier_deduction = min(outlier_ratio * 50.0, 15.0)
    outlier_score = max(0.0, 100.0 - (outlier_deduction / 15.0) * 100.0)

    total_deductions = comp_deduction + uniq_deduction + val_deduction + struct_deduction + outlier_deduction
    overall_score = max(0.0, min(100.0, round(100.0 - total_deductions, 1)))

    breakdown = {
        "completeness": round(comp_score, 1),
        "uniqueness": round(uniq_score, 1),
        "validity": round(val_score, 1),
        "structural": round(struct_score, 1),
        "outliers": round(outlier_score, 1),
        "overall_score": overall_score,
    }

    return overall_score, breakdown


# ─── Safe Cleaning Engine & Audit Trail ────────────────────────────

def perform_safe_cleaning(
    df: pd.DataFrame,
    quality_report: QualityReport,
    columns_meta_dict: Dict[str, ColumnMetadata]
) -> Tuple[pd.DataFrame, CleaningAudit]:
    """
    Perform safe, non-destructive, auditable cleaning operations.
    Leaves original input DataFrame completely untouched.
    Every operation records an explicit ActionRecord.
    """
    cleaned_df = df.copy(deep=True)
    applied_actions: List[ActionRecord] = []
    dropped_cols: List[str] = []
    imputed_cols: List[str] = []

    if cleaned_df.empty or len(cleaned_df.columns) == 0:
        return cleaned_df, CleaningAudit(
            original_shape=[int(df.shape[0]), int(df.shape[1])],
            cleaned_shape=[int(cleaned_df.shape[0]), int(cleaned_df.shape[1])],
            applied_actions=[],
            dropped_columns=[],
            imputed_columns=[],
        )

    # 1. Normalize Empty & Whitespace-only string values to NaN
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == object or pd.api.types.is_string_dtype(cleaned_df[col]):
            s = cleaned_df[col].dropna().astype(str)
            whitespace_mask = s.str.strip().eq("")
            whitespace_count = int(whitespace_mask.sum())
            if whitespace_count > 0:
                # Replace with np.nan
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: np.nan if (isinstance(x, str) and x.strip() == "") else x
                )
                applied_actions.append(ActionRecord(
                    action_type="normalize_missing_markers",
                    action="normalize_missing_markers",
                    column=col,
                    affected_rows=whitespace_count,
                    reason="empty_or_whitespace_strings",
                    method="convert_to_nan",
                    before_summary={"whitespace_missing_count": whitespace_count},
                    after_summary={"whitespace_missing_count": 0, "normalized_to_nan": True},
                    description=f"Normalized {whitespace_count} empty or whitespace-only string values in '{col}' to NaN.",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))

    # 2. Safe Leading/Trailing Whitespace Stripping for string columns
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == object or pd.api.types.is_string_dtype(cleaned_df[col]):
            s = cleaned_df[col].dropna()
            str_series = s[s.apply(lambda x: isinstance(x, str))]
            if len(str_series) > 0:
                untrimmed_mask = str_series != str_series.str.strip()
                untrimmed_count = int(untrimmed_mask.sum())
                if untrimmed_count > 0:
                    cleaned_df[col] = cleaned_df[col].apply(
                        lambda x: x.strip() if isinstance(x, str) else x
                    )
                    applied_actions.append(ActionRecord(
                        action_type="trim_whitespace",
                        action="trim_whitespace",
                        column=col,
                        affected_rows=untrimmed_count,
                        reason="inconsistent_leading_trailing_whitespace",
                        method="str_strip",
                        before_summary={"untrimmed_rows": untrimmed_count},
                        after_summary={"untrimmed_rows": 0},
                        description=f"Trimmed leading/trailing whitespace from {untrimmed_count} entries in '{col}'.",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    ))

    # 3. Drop Exact Duplicate Rows
    dup_rows = int(cleaned_df.duplicated().sum())
    if dup_rows > 0:
        before_rows = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        after_rows = len(cleaned_df)
        applied_actions.append(ActionRecord(
            action_type="drop_duplicates",
            action="drop_duplicates",
            column=None,
            affected_rows=dup_rows,
            reason="exact_duplicate_rows",
            method="drop_duplicates",
            before_summary={"total_rows": before_rows, "duplicate_rows": dup_rows},
            after_summary={"total_rows": after_rows, "duplicate_rows": 0},
            description=f"Removed {dup_rows} exact duplicate rows from dataset.",
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))

    # 4. Drop Columns with Excessive Missingness (> 70%)
    cols_to_evaluate = list(cleaned_df.columns)
    for col in cols_to_evaluate:
        col_missing = int(cleaned_df[col].isnull().sum())
        missing_pct = (col_missing / max(len(cleaned_df), 1)) * 100.0

        if missing_pct > DROP_COLUMN_MISSING_THRESHOLD:
            cleaned_df = cleaned_df.drop(columns=[col])
            dropped_cols.append(col)
            applied_actions.append(ActionRecord(
                action_type="drop_column",
                action="drop_column",
                column=col,
                affected_rows=len(cleaned_df),
                reason="excessive_missingness_above_70pct",
                method="drop_column",
                before_summary={"missing_count": col_missing, "missing_percentage": round(missing_pct, 2)},
                after_summary={"column_dropped": True},
                description=f"Dropped column '{col}' due to excessive missingness ({missing_pct:.1f}% missing).",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ))

    # 5. Safe Missing Value Imputation (when missing <= 50%)
    for col in list(cleaned_df.columns):
        col_missing = int(cleaned_df[col].isnull().sum())
        if col_missing == 0:
            continue

        missing_pct = (col_missing / max(len(cleaned_df), 1)) * 100.0
        if missing_pct > SAFE_IMPUTATION_MAX_MISSING:
            # Missingness is between 50% and 70%: leave as is with audit note / report warning
            continue

        meta = columns_meta_dict.get(col)
        # Numeric Imputation
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            # If boolean numeric
            if meta and meta.inferred_type == InferredDtype.BOOLEAN:
                mode_series = cleaned_df[col].mode()
                mode_val = int(mode_series.iloc[0]) if len(mode_series) > 0 else 0
                cleaned_df[col] = cleaned_df[col].fillna(mode_val)
                imputed_cols.append(col)
                applied_actions.append(ActionRecord(
                    action_type="impute_missing",
                    action="impute_missing",
                    column=col,
                    affected_rows=col_missing,
                    reason="boolean_missing_values",
                    method="mode",
                    before_summary={"missing_count": col_missing, "missing_percentage": round(missing_pct, 2)},
                    after_summary={"missing_count": 0, "imputed_value": mode_val},
                    description=f"Imputed {col_missing} missing values in boolean column '{col}' using mode ({mode_val}).",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))
            else:
                median_val = float(cleaned_df[col].median()) if not pd.isna(cleaned_df[col].median()) else 0.0
                if meta and meta.inferred_type == InferredDtype.NUMERIC_DISCRETE:
                    median_val = round(median_val)
                cleaned_df[col] = cleaned_df[col].fillna(median_val)
                imputed_cols.append(col)
                applied_actions.append(ActionRecord(
                    action_type="impute_missing",
                    action="impute_missing",
                    column=col,
                    affected_rows=col_missing,
                    reason="numeric_missing_values",
                    method="median",
                    before_summary={"missing_count": col_missing, "missing_percentage": round(missing_pct, 2)},
                    after_summary={"missing_count": 0, "imputed_value": median_val},
                    description=f"Imputed {col_missing} missing values in numeric column '{col}' using median ({median_val:.4g}).",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                ))
        # Boolean type
        elif meta and meta.inferred_type == InferredDtype.BOOLEAN:
            mode_series = cleaned_df[col].mode()
            mode_val = mode_series.iloc[0] if len(mode_series) > 0 else False
            cleaned_df[col] = cleaned_df[col].fillna(mode_val)
            imputed_cols.append(col)
            applied_actions.append(ActionRecord(
                action_type="impute_missing",
                action="impute_missing",
                column=col,
                affected_rows=col_missing,
                reason="boolean_missing_values",
                method="mode",
                before_summary={"missing_count": col_missing, "missing_percentage": round(missing_pct, 2)},
                after_summary={"missing_count": 0, "imputed_value": str(mode_val)},
                description=f"Imputed {col_missing} missing values in boolean column '{col}' using mode ({mode_val}).",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ))
        # Categorical / String Imputation
        else:
            mode_series = cleaned_df[col].mode()
            mode_val = str(mode_series.iloc[0]) if len(mode_series) > 0 else "Unknown"
            cleaned_df[col] = cleaned_df[col].fillna(mode_val)
            imputed_cols.append(col)
            applied_actions.append(ActionRecord(
                action_type="impute_missing",
                action="impute_missing",
                column=col,
                affected_rows=col_missing,
                reason="categorical_missing_values",
                method="mode",
                before_summary={"missing_count": col_missing, "missing_percentage": round(missing_pct, 2)},
                after_summary={"missing_count": 0, "imputed_value": mode_val},
                description=f"Imputed {col_missing} missing values in categorical column '{col}' using mode ('{mode_val}').",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ))

    cleaning_audit = CleaningAudit(
        original_shape=[int(df.shape[0]), int(df.shape[1])],
        cleaned_shape=[int(cleaned_df.shape[0]), int(cleaned_df.shape[1])],
        applied_actions=applied_actions,
        dropped_columns=dropped_cols,
        imputed_columns=imputed_cols,
    )

    return cleaned_df, cleaning_audit


# ─── Master Entry Point: evaluate_quality ──────────────────────────

def evaluate_quality(
    df: pd.DataFrame,
    columns_meta: Optional[List[ColumnMetadata]] = None
) -> Tuple[QualityReport, CleaningAudit, pd.DataFrame]:
    """
    Perform deep data quality evaluation and generate cleaning audit trail.

    Returns:
        (QualityReport, CleaningAudit, pd.DataFrame)
    """
    columns_meta_dict: Dict[str, ColumnMetadata] = {
        cm.name: cm for cm in (columns_meta or [])
    }

    total_rows = len(df)
    total_cols = len(df.columns)

    # 1. Missingness Analysis
    missing_res = analyze_missingness(df, columns_meta_dict)

    # 2. Duplicate Analysis
    dup_res = analyze_duplicates(df, columns_meta_dict)

    # 3. Constant & Near-Constant Analysis
    const_res = analyze_constants_and_near_constants(df, columns_meta_dict)

    # 4. High Cardinality Analysis
    high_card_res = analyze_high_cardinality(df, columns_meta_dict)

    # 5. Outlier Analysis
    outlier_res = analyze_numeric_outliers(df, columns_meta_dict)

    # 6. Categorical Quality & Type Mismatches
    cat_res = analyze_categorical_quality(df, columns_meta_dict)

    # 7. Quality Score Computation
    overall_score, score_breakdown = compute_explainable_quality_score(
        total_rows=total_rows,
        total_cols=total_cols,
        missingness_res=missing_res,
        duplicate_res=dup_res,
        constant_res=const_res,
        high_card_res=high_card_res,
        outlier_res=outlier_res,
        categorical_res=cat_res,
    )

    # Combine warnings and passed checks
    all_warnings = (
        dup_res["warnings"]
        + missing_res["warnings"]
        + const_res["warnings"]
        + high_card_res["warnings"]
        + outlier_res["warnings"]
        + cat_res["warnings"]
    )
    # Deduplicate warnings preserving order
    seen_warnings: Set[str] = set()
    deduped_warnings: List[str] = []
    for w in all_warnings:
        if w not in seen_warnings:
            seen_warnings.add(w)
            deduped_warnings.append(w)

    all_passed = (
        dup_res["passed_checks"]
        + missing_res["passed_checks"]
        + const_res["passed_checks"]
        + outlier_res["passed_checks"]
        + cat_res["passed_checks"]
    )
    seen_passed: Set[str] = set()
    deduped_passed: List[str] = []
    for p in all_passed:
        if p not in seen_passed:
            seen_passed.add(p)
            deduped_passed.append(p)

    quality_report = QualityReport(
        overall_quality_score=overall_score,
        score_breakdown=score_breakdown,
        duplicate_row_count=dup_res["duplicate_row_count"],
        duplicate_row_percentage=dup_res["duplicate_row_percentage"],
        unique_row_count=dup_res["unique_row_count"],
        total_missing_cells=missing_res["total_missing_cells"],
        missing_cell_percentage=missing_res["missing_cell_percentage"],
        columns_with_missing=missing_res["columns_with_missing"],
        column_missingness=missing_res["column_missingness"],
        columns_with_outliers=outlier_res["columns_with_outliers"],
        total_outliers=outlier_res["total_outliers"],
        outlier_details=outlier_res["outlier_details"],
        constant_columns=const_res["constant_columns"],
        near_constant_columns=const_res["near_constant_columns"],
        high_cardinality_issues=high_card_res["high_cardinality_issues"],
        categorical_inconsistencies=cat_res["categorical_inconsistencies"],
        type_mismatches=cat_res["type_mismatches"],
        warnings=deduped_warnings,
        passed_checks=deduped_passed,
    )

    # 8. Safe Cleaning Engine & Audit
    cleaned_df, cleaning_audit = perform_safe_cleaning(
        df=df,
        quality_report=quality_report,
        columns_meta_dict=columns_meta_dict,
    )

    return quality_report, cleaning_audit, cleaned_df
