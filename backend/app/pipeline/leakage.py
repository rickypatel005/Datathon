"""
Person 1: Leakage Hunter & Identifier Isolation Engine.
Identifies target-derived features, post-event data, temporal/future leakage,
identifier contamination, and suspiciously predictive signals.
Uses multi-signal evidence to distinguish confirmed leakage from legitimate strong predictors.
"""
import re
from typing import List, Dict, Any, Optional, Tuple, Set
import pandas as pd
import numpy as np

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
    TemporalProperties,
)


# ─── Naming Vocabulary Constants ───────────────────────────────────

POST_EVENT_KEYWORDS = {
    "post_event", "post_outcome", "post_incident", "collection", "recovery",
    "settlement", "resolution", "resolved", "charge_off", "charged_off",
    "default_date", "churn_date", "exit_date", "cancellation", "refund",
    "closed_reason", "failure_reason", "complaint", "audit_result",
    "investigation_outcome", "discharged", "repossession", "bankruptcy_filed",
    "payout", "claim_settled", "exit_interview", "post_action",
}

TARGET_DERIVED_KEYWORDS = {
    "target", "label", "outcome", "ground_truth", "prediction", "actual",
    "verdict", "true_class", "target_encoded", "derived_target", "is_churn",
    "churn_flag", "default_flag", "fraud_flag", "target_proxy",
}

FUTURE_KEYWORDS = {
    "future", "next_", "following_", "subsequent", "later_", "forecast_",
    "upcoming", "closing_date", "discharge_date", "completion_date",
}


# ─── Statistical Association Helpers ───────────────────────────────

def calculate_cramers_v(s1: pd.Series, s2: pd.Series) -> float:
    """Calculate Cramer's V for two categorical series (bounded 0.0 to 1.0)."""
    valid = s1.notnull() & s2.notnull()
    if valid.sum() < 5:
        return 0.0
    
    contingency = pd.crosstab(s1[valid], s2[valid])
    if contingency.empty or contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return 0.0

    n = contingency.sum().sum()
    if n == 0:
        return 0.0

    # Chi-square calculation
    row_sums = contingency.sum(axis=1).values
    col_sums = contingency.sum(axis=0).values
    expected = np.outer(row_sums, col_sums) / n

    chi2 = np.sum((contingency.values - expected) ** 2 / np.maximum(expected, 1e-9))
    min_dim = min(contingency.shape) - 1
    if min_dim == 0:
        return 0.0

    v = np.sqrt(chi2 / (n * min_dim))
    return float(np.clip(v, 0.0, 1.0))


def calculate_correlation_ratio(categories: pd.Series, values: pd.Series) -> float:
    """Calculate Correlation Ratio (eta) between a categorical and a continuous variable."""
    valid = categories.notnull() & values.notnull()
    if valid.sum() < 5:
        return 0.0

    cat_s = categories[valid]
    val_s = values[valid]

    grouped = val_s.groupby(cat_s)
    if len(grouped) < 2:
        return 0.0

    grand_mean = val_s.mean()
    total_ss = np.sum((val_s - grand_mean) ** 2)
    if total_ss == 0:
        return 0.0

    between_ss = sum(len(g) * (g.mean() - grand_mean) ** 2 for _, g in grouped)
    eta = np.sqrt(between_ss / total_ss)
    return float(np.clip(eta, 0.0, 1.0))


def check_exact_or_inverse_copy(
    feature_s: pd.Series,
    target_s: pd.Series
) -> Optional[Tuple[str, str]]:
    """
    Check if feature is an exact copy or exact inverse complement of the target.
    Returns: (leakage_subtype, description) or None.
    """
    valid = feature_s.notnull() & target_s.notnull()
    if valid.sum() < 3:
        return None

    f_valid = feature_s[valid]
    t_valid = target_s[valid]

    # 1. Direct Equality Check
    try:
        if (f_valid == t_valid).all():
            return "exact_target_copy", "Feature values are 100% identical to target across all non-null entries."
    except Exception:
        pass

    # 2. String representation equality
    try:
        if (f_valid.astype(str).str.strip().str.lower() == t_valid.astype(str).str.strip().str.lower()).all():
            return "exact_target_copy", "Feature string values identically match target values."
    except Exception:
        pass

    # 3. Numeric inverse / complement check (e.g. 0/1 inverted)
    if pd.api.types.is_numeric_dtype(f_valid) and pd.api.types.is_numeric_dtype(t_valid):
        # Binary complement (f == 1 - t)
        if set(t_valid.unique()).issubset({0, 1, 0.0, 1.0}):
            if (f_valid == (1 - t_valid)).all():
                return "binary_target_complement", "Feature is an exact 1-complement (inverted binary) of the target."
        # Negation (f == -t)
        if (f_valid == -t_valid).all():
            return "exact_target_negation", "Feature is an exact negation (-target) of the target."

    # 4. Boolean complement check
    if pd.api.types.is_bool_dtype(f_valid) and pd.api.types.is_bool_dtype(t_valid):
        if (f_valid == ~t_valid).all():
            return "boolean_target_inverse", "Feature is an exact boolean NOT inverse of the target."

    return None


# ─── Sub-Engine 1: Identifier Isolation ─────────────────────────────

def isolate_identifiers(
    df: pd.DataFrame,
    columns_meta: List[ColumnMetadata],
    primary_target: Optional[str]
) -> Tuple[List[IdentifierIsolation], List[LeakageCandidate], List[str]]:
    """
    Isolate semantic entity keys and high-uniqueness identifier columns.
    Generates structured recommendations to exclude identifiers from ML model feature sets.
    """
    identifiers: List[IdentifierIsolation] = []
    candidates: List[LeakageCandidate] = []
    recommended_drops: List[str] = []

    total_rows = len(df)
    if total_rows == 0:
        return identifiers, candidates, recommended_drops

    for meta in columns_meta:
        col = meta.name
        if col == primary_target:
            continue

        if meta.is_identifier or meta.inferred_type == InferredDtype.IDENTIFIER:
            id_type = meta.subtype or "entity_id"
            uniq_ratio = meta.cardinality_ratio

            # Association with target if computable
            target_assoc = None
            if primary_target and primary_target in df.columns:
                s = df[col].dropna()
                t = df[primary_target].dropna()
                common_idx = s.index.intersection(t.index)
                if len(common_idx) >= 5:
                    if pd.api.types.is_numeric_dtype(df[col]) and pd.api.types.is_numeric_dtype(df[primary_target]):
                        corr = float(df.loc[common_idx, col].corr(df.loc[common_idx, primary_target]))
                        if not np.isnan(corr):
                            target_assoc = round(corr, 4)
                    elif pd.api.types.is_numeric_dtype(df[primary_target]):
                        eta = calculate_correlation_ratio(df.loc[common_idx, col], df.loc[common_idx, primary_target])
                        target_assoc = round(eta, 4)
                    else:
                        v = calculate_cramers_v(df.loc[common_idx, col], df.loc[common_idx, primary_target])
                        target_assoc = round(v, 4)

            reason_desc = (
                f"Column '{col}' is an identifier ({id_type}) with {round(uniq_ratio*100, 1)}% unique values. "
                "Identifiers must be isolated to prevent model memorization and spurious overfitting."
            )

            identifiers.append(IdentifierIsolation(
                column=col,
                identifier_type=id_type,
                uniqueness_ratio=uniq_ratio,
                target_association=target_assoc,
                recommended_use="exclude_from_model",
                reason=reason_desc,
            ))

            candidates.append(LeakageCandidate(
                column=col,
                leakage_type=LeakageType.ID_LEAKAGE,
                risk_level=LeakageRiskLevel.HIGH if uniq_ratio > 0.8 else LeakageRiskLevel.MEDIUM,
                reason=reason_desc,
                reasons=[
                    f"Semantic type is '{meta.inferred_type.value}' ({id_type})",
                    f"Cardinality ratio is {uniq_ratio:.4f} ({meta.unique_count} distinct values)",
                    "Identifiers provide entity tracking but cause spurious memorization if fed to models",
                ],
                confidence=0.95,
                evidence={
                    "identifier_type": id_type,
                    "uniqueness_ratio": uniq_ratio,
                    "target_association": target_assoc,
                },
                recommendation="exclude_from_model",
                target_column=primary_target,
                correlation_with_target=target_assoc,
            ))

            recommended_drops.append(col)

    return identifiers, candidates, recommended_drops


# ─── Sub-Engine 2: Target-Derived & Post-Event Leakage ─────────────

def detect_target_derived_and_post_event(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata],
    target_candidate: TargetCandidate
) -> List[LeakageCandidate]:
    """
    Examine features against a target candidate for target copies, inverse encodings,
    name inclusions, post-event collection indicators, and extreme correlations.
    """
    candidates: List[LeakageCandidate] = []
    target_col = target_candidate.column_name

    if target_col not in df.columns:
        return candidates

    target_s = df[target_col]
    target_clean_name = re.sub(r"[^a-zA-Z0-9]", "", target_col.lower())

    for col in df.columns:
        if col == target_col:
            continue

        meta = columns_meta_dict.get(col)
        # Skip datetime columns: temporal engine handles post-event/future timestamps
        if meta and meta.inferred_type == InferredDtype.DATETIME:
            continue

        feature_s = df[col]
        col_lower = col.lower()
        col_clean = re.sub(r"[^a-zA-Z0-9]", "", col_lower)

        # 1. Direct Copy or Deterministic Inverse/Complement
        exact_match = check_exact_or_inverse_copy(feature_s, target_s)
        if exact_match is not None:
            subtype, desc = exact_match
            candidates.append(LeakageCandidate(
                column=col,
                leakage_type=LeakageType.TARGET_DERIVED,
                risk_level=LeakageRiskLevel.CRITICAL,
                reason=f"Column '{col}' is a confirmed deterministic equivalent of target '{target_col}' ({subtype}).",
                reasons=[
                    desc,
                    "Exact deterministic relationship invalidates supervised ML evaluation.",
                ],
                confidence=1.0,
                evidence={"subtype": subtype, "exact_match": True},
                recommendation="exclude_from_model",
                target_column=target_col,
                correlation_with_target=1.0 if "inverse" not in subtype and "complement" not in subtype else -1.0,
            ))
            continue

        # 2. Naming Signals: Post-Event Keywords
        has_post_event_name = any(kw in col_lower for kw in POST_EVENT_KEYWORDS)
        has_target_in_name = (target_clean_name in col_clean and len(target_clean_name) >= 3) or any(
            kw in col_lower for kw in TARGET_DERIVED_KEYWORDS
        )

        # Compute Statistical Association
        assoc_metric = "none"
        assoc_val = 0.0
        corr_val = None

        if pd.api.types.is_numeric_dtype(feature_s) and pd.api.types.is_numeric_dtype(target_s):
            valid = feature_s.notnull() & target_s.notnull()
            if valid.sum() > 5:
                corr = float(feature_s[valid].corr(target_s[valid]))
                if not np.isnan(corr):
                    assoc_metric = "pearson_correlation"
                    assoc_val = abs(corr)
                    corr_val = round(corr, 4)
        elif pd.api.types.is_numeric_dtype(feature_s) and not pd.api.types.is_numeric_dtype(target_s):
            # Numeric feature, Categorical target -> Correlation Ratio (eta)
            eta = calculate_correlation_ratio(target_s, feature_s)
            assoc_metric = "correlation_ratio_eta"
            assoc_val = eta
            corr_val = round(eta, 4)
        elif not pd.api.types.is_numeric_dtype(feature_s) and not pd.api.types.is_numeric_dtype(target_s):
            # Categorical feature, Categorical target -> Cramer's V
            v = calculate_cramers_v(feature_s, target_s)
            assoc_metric = "cramers_v"
            assoc_val = v
            corr_val = round(v, 4)
        else:
            # Categorical feature, Numeric target -> Correlation Ratio (eta)
            eta = calculate_correlation_ratio(feature_s, target_s)
            assoc_metric = "correlation_ratio_eta"
            assoc_val = eta
            corr_val = round(eta, 4)

        # 3. Post-Event Leakage Classification
        if has_post_event_name:
            if assoc_val >= 0.60:
                candidates.append(LeakageCandidate(
                    column=col,
                    leakage_type=LeakageType.POST_EVENT,
                    risk_level=LeakageRiskLevel.HIGH,
                    reason=f"Column '{col}' name indicates post-event collection and exhibits strong association ({assoc_metric} = {assoc_val:.3f}) with target '{target_col}'.",
                    reasons=[
                        f"Column name contains post-event vocabulary matching outcome workflow",
                        f"Measured {assoc_metric} of {assoc_val:.3f} with target '{target_col}'",
                        "Data collected after target occurrence invalidates real-time inference",
                    ],
                    confidence=0.92,
                    evidence={
                        "keyword_matched": True,
                        "association_metric": assoc_metric,
                        "association_value": assoc_val,
                    },
                    recommendation="exclude_from_model",
                    target_column=target_col,
                    correlation_with_target=corr_val,
                ))
                continue
            else:
                candidates.append(LeakageCandidate(
                    column=col,
                    leakage_type=LeakageType.POST_EVENT,
                    risk_level=LeakageRiskLevel.MEDIUM,
                    reason=f"Column '{col}' name suggests post-outcome information; review collection timeline.",
                    reasons=[
                        "Column naming implies post-event data",
                        f"Weak to moderate association ({assoc_metric} = {assoc_val:.3f}) with target '{target_col}'",
                        "Review whether this feature is known at prediction time",
                    ],
                    confidence=0.65,
                    evidence={"keyword_matched": True, "association_metric": assoc_metric, "association_value": assoc_val},
                    recommendation="review",
                    target_column=target_col,
                    correlation_with_target=corr_val,
                ))
                continue

        # 4. Target-Derived Naming with Strong Association
        if has_target_in_name and assoc_val >= 0.70:
            candidates.append(LeakageCandidate(
                column=col,
                leakage_type=LeakageType.TARGET_DERIVED,
                risk_level=LeakageRiskLevel.HIGH,
                reason=f"Column '{col}' name references target and has high association ({assoc_metric} = {assoc_val:.3f}).",
                reasons=[
                    f"Column name embeds target keywords",
                    f"Strong association ({assoc_metric} = {assoc_val:.3f}) suggests derived feature or target proxy",
                ],
                confidence=0.88,
                evidence={"name_match": True, "association_metric": assoc_metric, "association_value": assoc_val},
                recommendation="exclude_from_model",
                target_column=target_col,
                correlation_with_target=corr_val,
            ))
            continue

        # 5. Suspiciously Predictive Signals (False Positive Controlled)
        if assoc_val >= 0.98:
            # Extreme association: near deterministic
            candidates.append(LeakageCandidate(
                column=col,
                leakage_type=LeakageType.SUSPICIOUS_CORRELATION,
                risk_level=LeakageRiskLevel.HIGH,
                reason=f"Column '{col}' exhibits near-perfect association ({assoc_metric} = {assoc_val:.3f}) with target '{target_col}'. Likely a proxy or leakage.",
                reasons=[
                    f"Extremely high {assoc_metric} ({assoc_val:.3f}) with target",
                    "Near-deterministic relationships in tabular data typically indicate target proxy features",
                ],
                confidence=0.85,
                evidence={"association_metric": assoc_metric, "association_value": assoc_val},
                recommendation="exclude_from_model",
                target_column=target_col,
                correlation_with_target=corr_val,
            ))
        elif assoc_val >= 0.85:
            # High association: could be legitimate strong feature or leakage -> mark review / use_with_warning
            candidates.append(LeakageCandidate(
                column=col,
                leakage_type=LeakageType.SUSPICIOUS_PREDICTIVE,
                risk_level=LeakageRiskLevel.MEDIUM,
                reason=f"Column '{col}' has strong association ({assoc_metric} = {assoc_val:.3f}) with target '{target_col}'. Verify feature validity.",
                reasons=[
                    f"High predictive strength ({assoc_metric} = {assoc_val:.3f})",
                    "Feature may be a legitimate strong business driver or subtle leak; review recommended",
                ],
                confidence=0.60,
                evidence={"association_metric": assoc_metric, "association_value": assoc_val},
                recommendation="use_with_warning",
                target_column=target_col,
                correlation_with_target=corr_val,
            ))

    return candidates


# ─── Sub-Engine 3: Temporal & Future Leakage ────────────────────────

def detect_temporal_and_future_leakage(
    df: pd.DataFrame,
    columns_meta_dict: Dict[str, ColumnMetadata],
    temporal: Optional[TemporalProperties],
    primary_target: Optional[str]
) -> List[LeakageCandidate]:
    """
    Detect future timestamps, post-event date columns, and temporal ordering anomalies.
    Does NOT flag normal primary datetime columns used for ordering.
    """
    candidates: List[LeakageCandidate] = []
    if temporal is None and not any(meta.inferred_type == InferredDtype.DATETIME for meta in columns_meta_dict.values()):
        return candidates

    primary_time_col = temporal.temporal_column if temporal else None

    for col, meta in columns_meta_dict.items():
        if col == primary_target or col == primary_time_col:
            continue

        col_lower = col.lower()
        has_future_name = any(kw in col_lower for kw in FUTURE_KEYWORDS)

        # 1. Feature with explicit future naming
        if has_future_name:
            candidates.append(LeakageCandidate(
                column=col,
                leakage_type=LeakageType.FUTURE,
                risk_level=LeakageRiskLevel.HIGH,
                reason=f"Column '{col}' name indicates future/post-event information.",
                reasons=[
                    "Column name contains future-looking naming keywords",
                    "Features containing future information create temporal leakage",
                ],
                confidence=0.85,
                evidence={"keyword_matched": True},
                recommendation="exclude_from_model",
                target_column=primary_target,
                correlation_with_target=None,
            ))
            continue

        # 2. Secondary Datetime Columns (Check if occurring after primary time column)
        if meta.inferred_type == InferredDtype.DATETIME and primary_time_col and primary_time_col in df.columns:
            try:
                t_prim = pd.to_datetime(df[primary_time_col], errors="coerce")
                t_sec = pd.to_datetime(df[col], errors="coerce")

                valid = t_prim.notnull() & t_sec.notnull()
                if valid.sum() > 10:
                    # Check if secondary date is strictly after primary date in >= 90% of rows
                    after_mask = t_sec[valid] > t_prim[valid]
                    after_ratio = float(after_mask.mean())

                    if after_ratio >= 0.90 and any(kw in col_lower for kw in POST_EVENT_KEYWORDS | {"close", "end", "settle", "exit", "finish", "outcome"}):
                        candidates.append(LeakageCandidate(
                            column=col,
                            leakage_type=LeakageType.FUTURE,
                            risk_level=LeakageRiskLevel.HIGH,
                            reason=f"Timestamp column '{col}' systematically occurs after primary event '{primary_time_col}' ({round(after_ratio*100, 1)}% of rows).",
                            reasons=[
                                f"Dates in '{col}' occur after '{primary_time_col}' in {round(after_ratio*100, 1)}% of rows",
                                "Post-event timestamps constitute temporal leakage in predictive modeling",
                            ],
                            confidence=0.90,
                            evidence={
                                "primary_time_column": primary_time_col,
                                "after_event_ratio": round(after_ratio, 4),
                            },
                            recommendation="exclude_from_model",
                            target_column=primary_target,
                            correlation_with_target=None,
                        ))
            except Exception:
                pass

    return candidates


# ─── Master Entry Point: detect_leakage ────────────────────────────

def detect_leakage(
    df: pd.DataFrame,
    columns_meta: List[ColumnMetadata],
    target_candidates: List[TargetCandidate],
    temporal: Optional[TemporalProperties] = None
) -> LeakageReport:
    """
    Execute full multi-signal leakage audit across unseen dataset features.

    Returns:
        LeakageReport with categorized findings, identifier isolation,
        recommendation levels, and sanitized feature column lists.
    """
    columns_meta_dict = {cm.name: cm for cm in columns_meta}
    primary_target = target_candidates[0].column_name if target_candidates else None

    findings: List[LeakageCandidate] = []
    recommended_drops: List[str] = []
    warnings: List[str] = []

    # 1. Constant Column Leakage / Zero Variance
    for meta in columns_meta:
        col = meta.name
        if col == primary_target:
            continue
        if meta.is_constant:
            cand = LeakageCandidate(
                column=col,
                leakage_type=LeakageType.CONSTANT_LEAKAGE,
                risk_level=LeakageRiskLevel.LOW,
                reason=f"Column '{col}' has zero variance (constant value). Offers no predictive information.",
                reasons=["Column is 100% constant across all non-null rows"],
                confidence=1.0,
                evidence={"constant": True},
                recommendation="exclude_from_model",
                target_column=primary_target,
                correlation_with_target=0.0,
            )
            findings.append(cand)
            recommended_drops.append(col)

    # 2. Identifier Isolation & Identifier Contamination
    identifiers, id_candidates, id_drops = isolate_identifiers(
        df=df,
        columns_meta=columns_meta,
        primary_target=primary_target,
    )
    findings.extend(id_candidates)
    recommended_drops.extend(id_drops)

    # 3. Target Relationship Analysis (Target-Derived & Post-Event)
    if target_candidates:
        primary_t_cand = target_candidates[0]
        target_findings = detect_target_derived_and_post_event(
            df=df,
            columns_meta_dict=columns_meta_dict,
            target_candidate=primary_t_cand,
        )
        for cand in target_findings:
            if cand.column == primary_target:
                continue
            if not any(f.column == cand.column and f.target_column == cand.target_column for f in findings):
                findings.append(cand)
                if cand.recommendation == "exclude_from_model" and cand.column not in recommended_drops:
                    recommended_drops.append(cand.column)

    # 4. Temporal & Future Leakage
    temporal_findings = detect_temporal_and_future_leakage(
        df=df,
        columns_meta_dict=columns_meta_dict,
        temporal=temporal,
        primary_target=primary_target,
    )
    for cand in temporal_findings:
        if not any(f.column == cand.column for f in findings):
            findings.append(cand)
            if cand.recommendation == "exclude_from_model" and cand.column not in recommended_drops:
                recommended_drops.append(cand.column)

    # 5. Partition Findings into Excluded vs Review Sets
    excluded_features: List[str] = []
    review_features: List[str] = []

    for f in findings:
        if f.recommendation == "exclude_from_model":
            if f.column not in excluded_features:
                excluded_features.append(f.column)
            warnings.append(f"Leakage Risk [{f.risk_level.value.upper()}]: Exclude '{f.column}' ({f.leakage_type.value}) - {f.reason}")
        elif f.recommendation in ("review", "use_with_warning"):
            if f.column not in review_features:
                review_features.append(f.column)
            warnings.append(f"Predictive Warning [{f.risk_level.value.upper()}]: Review '{f.column}' ({f.leakage_type.value}) - {f.reason}")

    # 6. Overall Dataset Leakage Risk Determination
    overall_risk = LeakageRiskLevel.NONE
    if any(f.risk_level == LeakageRiskLevel.CRITICAL for f in findings):
        overall_risk = LeakageRiskLevel.CRITICAL
    elif any(f.risk_level == LeakageRiskLevel.HIGH for f in findings):
        overall_risk = LeakageRiskLevel.HIGH
    elif any(f.risk_level == LeakageRiskLevel.MEDIUM for f in findings):
        overall_risk = LeakageRiskLevel.MEDIUM
    elif any(f.risk_level == LeakageRiskLevel.LOW for f in findings):
        overall_risk = LeakageRiskLevel.LOW

    # 7. Compile Sanitized Feature Column Set
    all_drops = set(excluded_features)
    if primary_target:
        all_drops.add(primary_target)
    
    sanitized_features = [c for c in df.columns if c not in all_drops]

    # Deduplicate drops preserving order
    deduped_drops: List[str] = []
    for d in recommended_drops:
        if d not in deduped_drops:
            deduped_drops.append(d)

    return LeakageReport(
        has_leakage_risk=len(findings) > 0,
        overall_risk=overall_risk,
        leakage_candidates=findings,
        findings=findings,
        identifiers=identifiers,
        recommended_drops=deduped_drops,
        excluded_features=excluded_features,
        review_features=review_features,
        sanitized_feature_columns=sanitized_features,
        warnings=warnings,
    )
