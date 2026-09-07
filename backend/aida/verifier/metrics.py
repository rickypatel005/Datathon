"""Deterministic metric exactness validator.

Enforces that any numerical assertion made in an insight directly matches
the ground-truth value stored in the Discovery or Analysis contracts.
Zero LLM calculation permitted.
"""

from __future__ import annotations
import math
from typing import Any, Optional
from pydantic import BaseModel

from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.analysis_contract import AnalysisContract
from backend.aida.contracts.insight_contract import MetricClaim, VerificationCheckResult


def _resolve_nested_attr(obj: Any, path: str) -> Any:
    """Safely traverse a nested dictionary or Pydantic model via dot/bracket notation.

    Examples:
        'columns.price.distribution.mean'
        'models.0.evaluation_metrics.accuracy'
        'models[RandomForest].evaluation_metrics.f1'
    """
    if obj is None or not path:
        return None

    # Normalize delimiters
    normalized = path.replace("[", ".").replace("]", "")
    parts = [p.strip() for p in normalized.split(".") if p.strip()]

    current: Any = obj
    for part in parts:
        if current is None:
            return None

        # Case 1: Pydantic model
        if isinstance(current, BaseModel):
            if hasattr(current, part):
                current = getattr(current, part)
            elif hasattr(current, "model_dump"):
                dumped = current.model_dump()
                current = dumped.get(part)
            else:
                return None
        # Case 2: Dict
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                # Try case-insensitive dict lookup
                matched = False
                for k, v in current.items():
                    if str(k).lower() == part.lower():
                        current = v
                        matched = True
                        break
                if not matched:
                    return None
        # Case 3: List / Sequence
        elif isinstance(current, (list, tuple)):
            if part.isdigit():
                idx = int(part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                # Search list of objects/dicts by name or algorithm attribute
                matched_item = None
                for item in current:
                    if isinstance(item, BaseModel):
                        name = getattr(item, "model_name", None) or getattr(item, "name", None) or getattr(item, "algorithm", None)
                        if name and str(name).lower() == part.lower():
                            matched_item = item
                            break
                    elif isinstance(item, dict):
                        name = item.get("model_name") or item.get("name") or item.get("algorithm")
                        if name and str(name).lower() == part.lower():
                            matched_item = item
                            break
                if matched_item is not None:
                    current = matched_item
                else:
                    return None
        else:
            return None

    return current


def verify_metric_exactness(
    claim: MetricClaim,
    discovery_contract: Optional[DiscoveryContract] = None,
    analysis_contract: Optional[AnalysisContract] = None,
) -> VerificationCheckResult:
    """Deterministically check if a claimed metric matches ground truth within tolerance.

    Args:
        claim: MetricClaim containing metric_name, source_contract, entity_path, and claimed_value.
        discovery_contract: Ground truth DiscoveryContract from Person 1.
        analysis_contract: Ground truth AnalysisContract from Person 2.

    Returns:
        VerificationCheckResult with pass/fail boolean, ground truth value, and audit message.
    """
    root_obj: Any = None
    if claim.source_contract == "discovery":
        root_obj = discovery_contract
    elif claim.source_contract == "analysis":
        root_obj = analysis_contract

    if root_obj is None:
        return VerificationCheckResult(
            check_type="metric_exactness",
            passed=False,
            claimed_value=claim.claimed_value,
            verified_value=None,
            tolerance=claim.tolerance,
            evidence_source=f"{claim.source_contract}:{claim.entity_path}",
            message=f"Ground truth source contract '{claim.source_contract}' is not provided or null.",
            error_detail="Source contract missing in state",
        )

    resolved_value = _resolve_nested_attr(root_obj, claim.entity_path)

    if resolved_value is None:
        return VerificationCheckResult(
            check_type="metric_exactness",
            passed=False,
            claimed_value=claim.claimed_value,
            verified_value=None,
            tolerance=claim.tolerance,
            evidence_source=f"{claim.source_contract}:{claim.entity_path}",
            message=f"Path '{claim.entity_path}' could not be resolved in {claim.source_contract} contract.",
            error_detail="Entity path not found in contract schema",
        )

    # Comparison logic
    try:
        if isinstance(claim.claimed_value, (int, float)) and isinstance(resolved_value, (int, float)):
            claimed_num = float(claim.claimed_value)
            verified_num = float(resolved_value)
            diff = abs(claimed_num - verified_num)
            passed = diff <= claim.tolerance

            msg = (
                f"Metric exactness passed. Claimed: {claimed_num}, Verified: {verified_num} "
                f"(diff: {diff:.6f} <= tol: {claim.tolerance})"
                if passed
                else f"Metric exactness FAILED. Claimed: {claimed_num}, Verified: {verified_num} "
                     f"(diff: {diff:.6f} > tol: {claim.tolerance})"
            )
            return VerificationCheckResult(
                check_type="metric_exactness",
                passed=passed,
                claimed_value=claimed_num,
                verified_value=verified_num,
                tolerance=claim.tolerance,
                evidence_source=f"{claim.source_contract}:{claim.entity_path}",
                message=msg,
                error_detail=None if passed else f"Value difference {diff:.6f} exceeds tolerance {claim.tolerance}",
            )
        else:
            # String or boolean exact equality
            passed = str(claim.claimed_value).strip().lower() == str(resolved_value).strip().lower()
            return VerificationCheckResult(
                check_type="metric_exactness",
                passed=passed,
                claimed_value=claim.claimed_value,
                verified_value=resolved_value,
                tolerance=claim.tolerance,
                evidence_source=f"{claim.source_contract}:{claim.entity_path}",
                message="Exact match confirmed" if passed else f"Mismatch: expected '{resolved_value}', got '{claim.claimed_value}'",
                error_detail=None if passed else "Exact equality check failed",
            )
    except Exception as exc:
        return VerificationCheckResult(
            check_type="metric_exactness",
            passed=False,
            claimed_value=claim.claimed_value,
            verified_value=resolved_value,
            tolerance=claim.tolerance,
            evidence_source=f"{claim.source_contract}:{claim.entity_path}",
            message=f"Verification comparison error: {str(exc)}",
            error_detail=str(exc),
        )
