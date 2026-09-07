"""Deterministic correlation and trend validator.

Validates statistical correlation claims against Discovery Contract correlation matrices.
No LLM estimation or interpretation allowed.
"""

from __future__ import annotations
from typing import Optional, Literal
from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.insight_contract import VerificationCheckResult


def classify_correlation_strength(r: float) -> str:
    """Standard statistical categorization of Pearson/Spearman coefficients."""
    abs_r = abs(r)
    if abs_r >= 0.7:
        return "strong"
    elif abs_r >= 0.3:
        return "moderate"
    else:
        return "weak"


def verify_correlation_claim(
    feature_a: str,
    feature_b: str,
    discovery_contract: DiscoveryContract,
    claimed_r: Optional[float] = None,
    claimed_direction: Optional[Literal["positive", "negative", "neutral"]] = None,
    claimed_strength: Optional[Literal["strong", "moderate", "weak"]] = None,
    tolerance: float = 0.05,
) -> VerificationCheckResult:
    """Deterministically validates a correlation assertion between two dataset features.

    Args:
        feature_a: First feature name.
        feature_b: Second feature name.
        discovery_contract: Ingested Discovery Contract containing correlation matrix.
        claimed_r: Asserted numerical correlation coefficient (optional).
        claimed_direction: Asserted direction ('positive', 'negative', 'neutral') (optional).
        claimed_strength: Asserted qualitative strength ('strong', 'moderate', 'weak') (optional).
        tolerance: Allowed difference between asserted and true correlation.

    Returns:
        VerificationCheckResult with verification status and proof.
    """
    actual_r = discovery_contract.get_correlation(feature_a, feature_b)

    if actual_r is None:
        return VerificationCheckResult(
            check_type="correlation_validity",
            passed=False,
            claimed_value={"r": claimed_r, "direction": claimed_direction, "strength": claimed_strength},
            verified_value=None,
            tolerance=tolerance,
            evidence_source=f"discovery.correlations.matrix.{feature_a}.{feature_b}",
            message=f"Correlation between '{feature_a}' and '{feature_b}' was not found in discovery contract.",
            error_detail="Pairwise correlation absent from matrix",
        )

    failures = []

    # 1. Numerical verification
    if claimed_r is not None:
        diff = abs(float(claimed_r) - actual_r)
        if diff > tolerance:
            failures.append(f"Claimed r={claimed_r} differs from true r={actual_r:.4f} (diff: {diff:.4f} > tol: {tolerance})")

    # 2. Direction verification
    if claimed_direction is not None:
        actual_direction = "positive" if actual_r > 0.05 else ("negative" if actual_r < -0.05 else "neutral")
        if claimed_direction.lower() != actual_direction:
            failures.append(
                f"Claimed direction '{claimed_direction}' contradicts actual direction '{actual_direction}' (r={actual_r:.4f})"
            )

    # 3. Qualitative strength verification
    if claimed_strength is not None:
        actual_strength = classify_correlation_strength(actual_r)
        if claimed_strength.lower() != actual_strength:
            failures.append(
                f"Claimed strength '{claimed_strength}' contradicts statistical standard '{actual_strength}' for r={actual_r:.4f}"
            )

    passed = len(failures) == 0
    msg = (
        f"Correlation verified for ('{feature_a}', '{feature_b}'): r={actual_r:.4f} "
        f"({classify_correlation_strength(actual_r)} {'positive' if actual_r > 0 else 'negative'})."
        if passed
        else f"Correlation verification FAILED: {'; '.join(failures)}"
    )

    return VerificationCheckResult(
        check_type="correlation_validity",
        passed=passed,
        claimed_value={"r": claimed_r, "direction": claimed_direction, "strength": claimed_strength},
        verified_value=actual_r,
        tolerance=tolerance,
        evidence_source=f"discovery.correlations.matrix.{feature_a}.{feature_b}",
        message=msg,
        error_detail="; ".join(failures) if not passed else None,
    )
