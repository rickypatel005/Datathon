"""Deterministic feature importance and model ranking validator.

Ensures that claims like "Feature X is the primary driver" or
"Feature A contributes 32% importance" are mathematically verified
against trained model weights in the Analysis Contract.
"""

from __future__ import annotations
from typing import List, Optional
from backend.aida.contracts.analysis_contract import AnalysisContract
from backend.aida.contracts.insight_contract import VerificationCheckResult


def verify_feature_importance_value(
    model_name: str,
    feature_name: str,
    analysis_contract: AnalysisContract,
    claimed_importance: float,
    tolerance: float = 0.02,
) -> VerificationCheckResult:
    """Validate a single feature's numeric importance score."""
    model = analysis_contract.get_model(model_name)
    if not model:
        return VerificationCheckResult(
            check_type="feature_importance_ranking",
            passed=False,
            claimed_value=claimed_importance,
            verified_value=None,
            tolerance=tolerance,
            evidence_source=f"analysis.models.{model_name}.feature_importances.{feature_name}",
            message=f"Model '{model_name}' not found in analysis contract.",
            error_detail="Model missing in contract",
        )

    if not model.feature_importances or feature_name not in model.feature_importances:
        return VerificationCheckResult(
            check_type="feature_importance_ranking",
            passed=False,
            claimed_value=claimed_importance,
            verified_value=None,
            tolerance=tolerance,
            evidence_source=f"analysis.models.{model_name}.feature_importances.{feature_name}",
            message=f"Feature '{feature_name}' has no recorded importance for model '{model_name}'.",
            error_detail="Feature not found in model importances",
        )

    actual_importance = float(model.feature_importances[feature_name])
    diff = abs(claimed_importance - actual_importance)
    passed = diff <= tolerance

    msg = (
        f"Feature '{feature_name}' importance verified: {actual_importance:.4f} (claimed: {claimed_importance})"
        if passed
        else f"Feature '{feature_name}' importance mismatch: claimed {claimed_importance}, actual {actual_importance:.4f} "
             f"(diff: {diff:.4f} > tol: {tolerance})"
    )

    return VerificationCheckResult(
        check_type="feature_importance_ranking",
        passed=passed,
        claimed_value=claimed_importance,
        verified_value=actual_importance,
        tolerance=tolerance,
        evidence_source=f"analysis.models.{model_name}.feature_importances.{feature_name}",
        message=msg,
        error_detail=None if passed else f"Importance difference {diff:.4f} exceeds tolerance {tolerance}",
    )


def verify_top_features_ranking(
    model_name: str,
    claimed_top_features: List[str],
    analysis_contract: AnalysisContract,
    top_n: Optional[int] = None,
) -> VerificationCheckResult:
    """Validate that the claimed top features match the true descending ranking.

    Args:
        model_name: Target model name or algorithm.
        claimed_top_features: Ordered list of feature names asserted to be top drivers.
        analysis_contract: Ingested Analysis Contract.
        top_n: Number of top features to verify against (defaults to len(claimed_top_features)).
    """
    model = analysis_contract.get_model(model_name)
    n = top_n or len(claimed_top_features)

    if not model or not model.feature_importances:
        return VerificationCheckResult(
            check_type="feature_importance_ranking",
            passed=False,
            claimed_value=claimed_top_features,
            verified_value=None,
            tolerance=0.0,
            evidence_source=f"analysis.models.{model_name}.feature_importances",
            message=f"Model '{model_name}' or its feature importances are missing from contract.",
            error_detail="Model importances absent",
        )

    actual_ranked_pairs = model.get_ranked_features(top_n=n)
    actual_top_features = [feat for feat, _ in actual_ranked_pairs]

    # Verify exact match in ranking order
    if len(claimed_top_features) != len(actual_top_features):
        passed = False
        reason = f"Ranked count mismatch: claimed {len(claimed_top_features)}, actual top {len(actual_top_features)}"
    elif [f.lower() for f in claimed_top_features] == [f.lower() for f in actual_top_features]:
        passed = True
        reason = None
    else:
        passed = False
        reason = f"Order mismatch: claimed {claimed_top_features}, true top {n} are {actual_top_features}"

    msg = (
        f"Top {n} feature ranking verified for '{model_name}': {actual_top_features}"
        if passed
        else f"Top feature ranking FAILED for '{model_name}': {reason}"
    )

    return VerificationCheckResult(
        check_type="feature_importance_ranking",
        passed=passed,
        claimed_value=claimed_top_features,
        verified_value=actual_top_features,
        tolerance=0.0,
        evidence_source=f"analysis.models.{model_name}.feature_importances",
        message=msg,
        error_detail=reason,
    )
