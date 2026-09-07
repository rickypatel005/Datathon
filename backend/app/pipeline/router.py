"""
Person 1: Intelligent Dataset & Task Router Engine.
Examines deep dataset understanding (fingerprint, schema, quality, targets, temporal, leakage)
and deterministically routes applicable analytical tasks, validation strategies, feature partitions,
and evaluation metrics with explainable evidence.
"""
from typing import List, Dict, Any, Optional, Set
import pandas as pd
import numpy as np

from app.contracts.discovery import (
    RouterDecision,
    TaskRouteDecision,
    DatasetFingerprint,
    TargetCandidate,
    QualityReport,
    LeakageReport,
    ColumnMetadata,
    TaskType,
    ValidationStrategy,
    InferredDtype,
)


def _partition_features(
    fingerprint: DatasetFingerprint,
    target_candidate: Optional[TargetCandidate],
    quality_report: QualityReport,
    leakage_report: Optional[LeakageReport],
    columns_meta: Optional[List[ColumnMetadata]],
) -> Dict[str, List[str]]:
    """
    Partition dataset features into clean, explainable operational sets:
      - usable_feature_columns
      - excluded_identifier_columns
      - excluded_leakage_columns
      - review_feature_columns
      - unsupported_feature_columns
    """
    all_columns: List[str] = (
        fingerprint.numeric_columns
        + fingerprint.categorical_columns
        + fingerprint.datetime_columns
        + fingerprint.identifier_columns
        + fingerprint.text_columns
    )
    # Deduplicate preserving order
    seen: Set[str] = set()
    deduped_cols: List[str] = []
    for c in all_columns:
        if c not in seen:
            seen.add(c)
            deduped_cols.append(c)

    target_name = target_candidate.column_name if target_candidate else None

    # 1. Identifiers
    excluded_identifiers = set()
    if leakage_report and leakage_report.identifiers:
        excluded_identifiers.update(i.column for i in leakage_report.identifiers)
    else:
        excluded_identifiers.update(fingerprint.identifier_columns)

    # 2. Excluded Leakage
    excluded_leakage = set()
    review_features = set()
    if leakage_report:
        excluded_leakage.update(leakage_report.excluded_features)
        review_features.update(leakage_report.review_features)

    # 3. Unsupported Features (Constant / All-Null)
    unsupported_features = set()
    unsupported_features.update(fingerprint.constant_columns)
    if quality_report and quality_report.constant_columns:
        unsupported_features.update(c["column"] for c in quality_report.constant_columns)
    if quality_report and quality_report.column_missingness:
        for col, meta in quality_report.column_missingness.items():
            if meta.get("missing_percentage", 0.0) >= 99.0:
                unsupported_features.add(col)

    # 4. Usable Features (Non-target, non-ID, non-leakage, non-unsupported)
    drop_set = excluded_identifiers | excluded_leakage | unsupported_features
    if target_name:
        drop_set.add(target_name)

    usable_features = [c for c in deduped_cols if c not in drop_set]

    return {
        "usable_feature_columns": usable_features,
        "excluded_identifier_columns": sorted(list(excluded_identifiers)),
        "excluded_leakage_columns": sorted(list(excluded_leakage - excluded_identifiers)),
        "review_feature_columns": sorted(list(review_features)),
        "unsupported_feature_columns": sorted(list(unsupported_features)),
    }


def _discover_grouping_column(
    columns_meta: Optional[List[ColumnMetadata]],
    primary_target: Optional[str]
) -> Optional[str]:
    """
    Identify potential entity grouping column (e.g. group_id, store_id, hospital_id, region, batch)
    for GroupKFold validation strategy recommendations.
    """
    if not columns_meta:
        return None

    group_keywords = ["group", "cluster", "batch", "region", "store", "hospital", "site", "subject", "account", "dept", "department"]

    for meta in columns_meta:
        if meta.name == primary_target:
            continue
        col_lower = meta.name.lower()
        if any(kw in col_lower for kw in group_keywords):
            # Check cardinality: moderate distinct groups (between 2 and 50 groups)
            if 2 <= meta.unique_count <= 50 and meta.cardinality_ratio < 0.5:
                return meta.name

    return None


def route_dataset(
    fingerprint: DatasetFingerprint,
    target_candidates: List[TargetCandidate],
    quality_report: QualityReport,
    leakage_report: Optional[LeakageReport] = None,
    columns_meta: Optional[List[ColumnMetadata]] = None,
) -> RouterDecision:
    """
    Intelligent, deterministic, leakage-aware Dataset & Task Router.
    Routes applicable analytical capabilities, validation strategies, metric suites, and feature partitions.
    """
    total_rows = fingerprint.shape[0]
    total_cols = fingerprint.shape[1]

    # Primary target candidate
    primary_candidate: Optional[TargetCandidate] = target_candidates[0] if target_candidates else None
    primary_target_name: Optional[str] = primary_candidate.column_name if primary_candidate else None

    # Partition features
    feature_partitions = _partition_features(
        fingerprint=fingerprint,
        target_candidate=primary_candidate,
        quality_report=quality_report,
        leakage_report=leakage_report,
        columns_meta=columns_meta,
    )
    usable_features = feature_partitions["usable_feature_columns"]
    group_col = _discover_grouping_column(columns_meta, primary_target_name)

    # Temporal properties
    temporal = fingerprint.temporal
    has_temporal = temporal is not None and temporal.temporal_column is not None

    task_decisions: Dict[str, TaskRouteDecision] = {}
    applicable_engines: List[str] = ["statistical_engine"]
    skipped_engines: Dict[str, str] = {}
    secondary_tasks: List[TaskType] = []

    # ─── Route 1: Descriptive Statistics ──────────────────────────────
    if total_rows > 0 and total_cols > 0:
        task_decisions["descriptive_statistics"] = TaskRouteDecision(
            task="descriptive_statistics",
            status="applicable",
            reason="Dataset contains structured tabular records suitable for descriptive profiling.",
            evidence={"row_count": total_rows, "column_count": total_cols},
            confidence=1.0,
            recommended_metrics=["mean", "std", "median", "skewness", "kurtosis", "iqr"],
        )
    else:
        task_decisions["descriptive_statistics"] = TaskRouteDecision(
            task="descriptive_statistics",
            status="insufficient_evidence",
            reason="Dataset has 0 rows or 0 columns.",
            evidence={"row_count": total_rows, "column_count": total_cols},
            confidence=0.0,
        )

    # ─── Route 2: Correlation & Association Analysis ───────────────────
    if len(usable_features) >= 2:
        task_decisions["correlation_analysis"] = TaskRouteDecision(
            task="correlation_analysis",
            status="applicable",
            reason=f"Sufficient usable feature pairs ({len(usable_features)} non-identifier features) available for correlation/association analysis.",
            evidence={"usable_feature_count": len(usable_features)},
            confidence=1.0,
            recommended_metrics=["pearson", "spearman", "cramers_v"],
        )
    else:
        task_decisions["correlation_analysis"] = TaskRouteDecision(
            task="correlation_analysis",
            status="insufficient_evidence",
            reason=f"Fewer than 2 usable features available ({len(usable_features)} usable features).",
            evidence={"usable_feature_count": len(usable_features)},
            confidence=0.0,
        )

    # ─── Route 3: Binary Classification ────────────────────────────────
    is_binary_target = (
        primary_candidate is not None
        and primary_candidate.task_type == TaskType.BINARY_CLASSIFICATION
        and primary_candidate.confidence_score >= 0.50
    )
    if is_binary_target:
        cb = fingerprint.class_balance
        is_imbalanced = cb.is_imbalanced if cb else False
        minority_pct = cb.minority_class_percentage if cb else 50.0

        bin_metrics = ["roc_auc", "pr_auc", "f1_weighted", "precision", "recall", "log_loss", "balanced_accuracy"]
        bin_val = "StratifiedKFold"
        if is_imbalanced:
            bin_val_reason = f"Target '{primary_candidate.column_name}' has class imbalance (minority class {minority_pct:.1f}%). StratifiedKFold required to preserve class ratios."
        else:
            bin_val_reason = "Binary classification requires StratifiedKFold cross-validation."

        task_decisions["binary_classification"] = TaskRouteDecision(
            task="binary_classification",
            status="applicable",
            reason=f"Binary categorical target '{primary_candidate.column_name}' detected with {primary_candidate.class_count or 2} discrete classes.",
            evidence={
                "target_column": primary_candidate.column_name,
                "confidence": primary_candidate.confidence_score,
                "minority_class_percentage": minority_pct,
                "is_imbalanced": is_imbalanced,
            },
            confidence=primary_candidate.confidence_score,
            target_column=primary_candidate.column_name,
            recommended_validation=bin_val,
            recommended_metrics=bin_metrics,
        )
        applicable_engines.extend(["classification_championship", "error_analysis", "subgroup_analysis"])
    else:
        reason_skip = (
            f"Primary target '{primary_candidate.column_name}' is {primary_candidate.task_type.value} (not binary)."
            if primary_candidate else "No supervised target candidate detected."
        )
        task_decisions["binary_classification"] = TaskRouteDecision(
            task="binary_classification",
            status="skipped",
            reason=reason_skip,
            evidence={"primary_candidate": primary_candidate.model_dump() if primary_candidate else None},
        )
        skipped_engines["binary_classification"] = reason_skip

    # ─── Route 4: Multiclass Classification ────────────────────────────
    is_multiclass_target = (
        primary_candidate is not None
        and primary_candidate.task_type == TaskType.MULTICLASS_CLASSIFICATION
        and primary_candidate.confidence_score >= 0.50
    )
    if is_multiclass_target:
        task_decisions["multiclass_classification"] = TaskRouteDecision(
            task="multiclass_classification",
            status="applicable",
            reason=f"Multiclass categorical target '{primary_candidate.column_name}' detected with {primary_candidate.class_count} distinct categories.",
            evidence={
                "target_column": primary_candidate.column_name,
                "class_count": primary_candidate.class_count,
                "confidence": primary_candidate.confidence_score,
            },
            confidence=primary_candidate.confidence_score,
            target_column=primary_candidate.column_name,
            recommended_validation="StratifiedKFold",
            recommended_metrics=["f1_weighted", "roc_auc_ovr", "precision_weighted", "recall_weighted", "log_loss", "balanced_accuracy"],
        )
        applicable_engines.extend(["classification_championship", "error_analysis", "subgroup_analysis"])
    else:
        reason_skip = (
            f"Primary target is {primary_candidate.task_type.value} (not multiclass)."
            if primary_candidate else "No supervised target candidate detected."
        )
        task_decisions["multiclass_classification"] = TaskRouteDecision(
            task="multiclass_classification",
            status="skipped",
            reason=reason_skip,
            evidence={"primary_candidate": primary_candidate.model_dump() if primary_candidate else None},
        )

    # ─── Route 5: Regression ───────────────────────────────────────────
    is_regression_target = (
        primary_candidate is not None
        and primary_candidate.task_type == TaskType.REGRESSION
        and primary_candidate.confidence_score >= 0.40
    )
    if is_regression_target:
        reg_val = "TimeSeriesSplit" if has_temporal else "KFold"
        reg_val_reason = (
            f"Temporal ordering present in '{temporal.temporal_column}'; TimeSeriesSplit assigned."
            if has_temporal else "Continuous regression target uses standard 5-Fold cross-validation."
        )
        task_decisions["regression"] = TaskRouteDecision(
            task="regression",
            status="applicable",
            reason=f"Continuous numeric target '{primary_candidate.column_name}' detected with suitable continuous variance.",
            evidence={
                "target_column": primary_candidate.column_name,
                "confidence": primary_candidate.confidence_score,
            },
            confidence=primary_candidate.confidence_score,
            target_column=primary_candidate.column_name,
            recommended_validation=reg_val,
            recommended_metrics=["rmse", "r2_score", "mae", "mape", "explained_variance"],
        )
        applicable_engines.extend(["regression_engine", "error_analysis", "residual_analysis"])
    else:
        reason_skip = (
            f"Primary target is {primary_candidate.task_type.value} (not continuous numeric regression)."
            if primary_candidate else "No continuous numeric target candidate detected."
        )
        task_decisions["regression"] = TaskRouteDecision(
            task="regression",
            status="skipped",
            reason=reason_skip,
            evidence={"primary_candidate": primary_candidate.model_dump() if primary_candidate else None},
        )
        skipped_engines["regression_engine"] = reason_skip

    # ─── Route 6: Time-Series Forecasting ──────────────────────────────
    if has_temporal:
        distinct_dates = temporal.distinct_dates_count or 0
        numeric_count = len(fingerprint.numeric_columns)

        if distinct_dates >= 10 and total_rows >= 15 and numeric_count >= 1:
            task_decisions["time_series_forecasting"] = TaskRouteDecision(
                task="time_series_forecasting",
                status="applicable",
                reason=f"Ordered temporal structure in '{temporal.temporal_column}' with {distinct_dates} distinct timestamps and {numeric_count} numeric metric series.",
                evidence={
                    "temporal_column": temporal.temporal_column,
                    "distinct_timestamps": distinct_dates,
                    "is_sorted": temporal.is_sorted,
                    "inferred_frequency": temporal.inferred_frequency,
                },
                confidence=0.90,
                recommended_validation="TimeSeriesSplit",
                recommended_metrics=["rmse", "mae", "mape", "smape"],
            )
            applicable_engines.append("time_series_forecasting")
        elif distinct_dates < 10 or total_rows < 15:
            reason_skip = f"Datetime column '{temporal.temporal_column}' exists, but fewer than minimum distinct timestamps (detected {distinct_dates}, minimum 10 required) for reliable forecasting."
            task_decisions["time_series_forecasting"] = TaskRouteDecision(
                task="time_series_forecasting",
                status="insufficient_evidence",
                reason=reason_skip,
                evidence={"temporal_column": temporal.temporal_column, "distinct_timestamps": distinct_dates},
            )
            skipped_engines["time_series_forecasting"] = reason_skip
        else:
            reason_skip = "Temporal column exists, but no numeric continuous metrics are available to forecast."
            task_decisions["time_series_forecasting"] = TaskRouteDecision(
                task="time_series_forecasting",
                status="insufficient_evidence",
                reason=reason_skip,
                evidence={"numeric_columns": numeric_count},
            )
            skipped_engines["time_series_forecasting"] = reason_skip
    else:
        reason_skip = "No datetime/temporal column detected in dataset."
        task_decisions["time_series_forecasting"] = TaskRouteDecision(
            task="time_series_forecasting",
            status="skipped",
            reason=reason_skip,
            evidence={"candidate_date_columns": []},
        )
        skipped_engines["time_series_forecasting"] = reason_skip

    # ─── Route 7: Clustering / Unsupervised EDA ────────────────────────
    if len(usable_features) >= 2:
        task_decisions["clustering"] = TaskRouteDecision(
            task="clustering",
            status="applicable",
            reason=f"Dataset contains {len(usable_features)} usable features suitable for unsupervised clustering and latent space analysis.",
            evidence={"usable_feature_count": len(usable_features)},
            confidence=0.85,
            recommended_validation="StandardSplit",
            recommended_metrics=["silhouette_score", "davies_bouldin_score", "calinski_harabasz_score"],
        )
        applicable_engines.extend(["clustering_engine", "pca_dimensionality_engine"])
    else:
        task_decisions["clustering"] = TaskRouteDecision(
            task="clustering",
            status="insufficient_evidence",
            reason=f"Insufficient usable features ({len(usable_features)} usable features found; minimum 2 required, excluding identifiers/constants/leakage).",
            evidence={"usable_feature_count": len(usable_features)},
        )

    # ─── Primary Task & Validation Strategy Selection ──────────────────
    if is_binary_target:
        primary_task = TaskType.BINARY_CLASSIFICATION
        secondary_tasks = [TaskType.CLUSTERING, TaskType.UNSUPERVISED_EDA]
        validation_strategy = ValidationStrategy.STRATIFIED_K_FOLD
        metrics = task_decisions["binary_classification"].recommended_metrics
        val_rationale = (
            f"Binary classification on target '{primary_candidate.column_name}'. "
            f"Stratified 5-Fold validation assigned to preserve class ratios."
        )
        rationale = (
            f"Binary classification routed for target '{primary_candidate.column_name}' "
            f"({primary_candidate.class_count or 2} classes). Stratified 5-Fold cross-validation is required."
        )
    elif is_multiclass_target:
        primary_task = TaskType.MULTICLASS_CLASSIFICATION
        secondary_tasks = [TaskType.CLUSTERING, TaskType.UNSUPERVISED_EDA]
        validation_strategy = ValidationStrategy.STRATIFIED_K_FOLD
        metrics = task_decisions["multiclass_classification"].recommended_metrics
        val_rationale = f"Multiclass classification on target '{primary_candidate.column_name}'. Stratified 5-Fold validation assigned."
        rationale = f"Multiclass classification routed for target '{primary_candidate.column_name}' with {primary_candidate.class_count} distinct categories."
    elif is_regression_target:
        primary_task = TaskType.REGRESSION
        secondary_tasks = [TaskType.CLUSTERING, TaskType.UNSUPERVISED_EDA]
        if has_temporal and task_decisions["time_series_forecasting"].status == "applicable":
            validation_strategy = ValidationStrategy.TIME_SERIES_SPLIT
            val_rationale = f"Continuous target '{primary_candidate.column_name}' has temporal ordering in '{temporal.temporal_column}'. TimeSeriesSplit assigned."
            secondary_tasks.append(TaskType.TIME_SERIES_FORECASTING)
        else:
            validation_strategy = ValidationStrategy.K_FOLD
            val_rationale = f"Continuous numeric target '{primary_candidate.column_name}' uses standard 5-Fold cross-validation."
        metrics = task_decisions["regression"].recommended_metrics
        rationale = f"Regression analysis routed for numeric continuous target '{primary_candidate.column_name}'."
    elif task_decisions["time_series_forecasting"].status == "applicable":
        primary_task = TaskType.TIME_SERIES_FORECASTING
        secondary_tasks = [TaskType.CLUSTERING, TaskType.UNSUPERVISED_EDA]
        validation_strategy = ValidationStrategy.TIME_SERIES_SPLIT
        metrics = ["rmse", "mae", "mape", "smape"]
        val_rationale = f"Temporal structure in '{temporal.temporal_column}' requires TimeSeriesSplit validation."
        rationale = f"Time-series forecasting routed for temporal series '{temporal.temporal_column}' with {temporal.distinct_dates_count} timestamps."
    elif task_decisions["clustering"].status == "applicable":
        primary_task = TaskType.CLUSTERING
        secondary_tasks = [TaskType.UNSUPERVISED_EDA]
        validation_strategy = ValidationStrategy.STANDARD_SPLIT
        metrics = ["silhouette_score", "davies_bouldin_score", "calinski_harabasz_score"]
        val_rationale = "Unsupervised clustering uses standard train/validation split."
        rationale = f"Dataset contains no evident supervised target. Routed to clustering across {len(usable_features)} usable features."
    else:
        primary_task = TaskType.UNSUPERVISED_EDA
        secondary_tasks = []
        validation_strategy = ValidationStrategy.STANDARD_SPLIT
        metrics = ["mean", "std", "skewness"]
        val_rationale = "Exploratory data analysis without supervised target."
        rationale = "Dataset routed to exploratory descriptive analysis."

    # Grouped data validation adaptation
    if group_col and validation_strategy in (ValidationStrategy.K_FOLD, ValidationStrategy.STRATIFIED_K_FOLD):
        validation_strategy = ValidationStrategy.GROUP_K_FOLD
        val_rationale = f"Entity grouping variable '{group_col}' detected. GroupKFold recommended to prevent cross-group leakage."
        rationale += f" GroupKFold assigned on '{group_col}'."

    # Deduplicate engines preserving order
    deduped_engines: List[str] = []
    seen_eng: Set[str] = set()
    for eng in applicable_engines:
        if eng not in seen_eng:
            seen_eng.add(eng)
            deduped_engines.append(eng)

    # Deduplicate secondary tasks
    deduped_secondary: List[TaskType] = []
    seen_sec: Set[TaskType] = {primary_task}
    for t in secondary_tasks:
        if t not in seen_sec:
            seen_sec.add(t)
            deduped_secondary.append(t)

    return RouterDecision(
        recommended_primary_task=primary_task,
        secondary_tasks=deduped_secondary,
        applicable_engines=deduped_engines,
        skipped_engines=skipped_engines,
        validation_strategy=validation_strategy,
        recommended_metrics=metrics,
        rationale=rationale,
        task_decisions=task_decisions,
        usable_feature_columns=usable_features,
        excluded_identifier_columns=feature_partitions["excluded_identifier_columns"],
        excluded_leakage_columns=feature_partitions["excluded_leakage_columns"],
        review_feature_columns=feature_partitions["review_feature_columns"],
        unsupported_feature_columns=feature_partitions["unsupported_feature_columns"],
        validation_rationale=val_rationale,
        group_column=group_col,
    )
