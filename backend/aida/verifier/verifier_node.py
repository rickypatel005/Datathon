"""Verifier Node for AIDA LangGraph Pipeline.

The Core of the Trust Layer.
Deterministically verifies all candidate insights against Discovery and Analysis contracts.
Routes valid insights to verified_insights with deterministic confidence scores,
and invalid insights to rejected_insights for complete auditability.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from backend.aida.state import AidaState, CritiqueEvaluation
from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.analysis_contract import AnalysisContract
from backend.aida.contracts.insight_contract import (
    CandidateInsight,
    VerifiedInsight,
    RejectedInsight,
    VerificationCheckResult,
    InsightContract,
)
from backend.aida.verifier.metrics import verify_metric_exactness
from backend.aida.verifier.correlations import verify_correlation_claim
from backend.aida.verifier.feature_importance import (
    verify_feature_importance_value,
    verify_top_features_ranking,
)
from backend.aida.verifier.confidence import calculate_deterministic_confidence


def verify_single_candidate(
    candidate: CandidateInsight,
    discovery: Optional[DiscoveryContract],
    analysis: Optional[AnalysisContract],
    critique: Optional[CritiqueEvaluation] = None,
) -> VerifiedInsight | RejectedInsight:
    """Run comprehensive deterministic verification suite on a single candidate insight.

    Never crashes. Returns either a VerifiedInsight or a RejectedInsight.
    """
    all_checks: List[VerificationCheckResult] = []

    # 1. Critic Gate
    if critique and not critique.is_approved_for_verification:
        return RejectedInsight(
            insight_id=candidate.insight_id,
            title=candidate.title,
            claim=candidate.claim,
            insight_type=candidate.insight_type,
            rejection_reason=f"Rejected by Critic: {critique.critique_notes}",
            failed_checks=[],
            all_checks=[],
        )

    # 2. Metric Claims Verification
    for metric_claim in candidate.metric_claims:
        check_result = verify_metric_exactness(
            claim=metric_claim,
            discovery_contract=discovery,
            analysis_contract=analysis,
        )
        all_checks.append(check_result)

    # 3. Type-Specific Deterministic Checks
    if candidate.insight_type == "correlation" and discovery:
        # Check if features are specified in entities_involved
        if len(candidate.entities_involved) >= 2:
            feat_a = candidate.entities_involved[0]
            feat_b = candidate.entities_involved[1]
            corr_check = verify_correlation_claim(
                feature_a=feat_a,
                feature_b=feat_b,
                discovery_contract=discovery,
            )
            all_checks.append(corr_check)

    # 4. Golden Rule Evaluation
    failed_checks = [c for c in all_checks if not c.passed]

    # If the candidate has numbers or claims to be verified but has no checks performed:
    if not all_checks and candidate.insight_type in ("correlation", "feature_importance", "model_performance", "anomaly"):
        return RejectedInsight(
            insight_id=candidate.insight_id,
            title=candidate.title,
            claim=candidate.claim,
            insight_type=candidate.insight_type,
            rejection_reason="Candidate lacked verifiable numerical claims or references required for its insight type.",
            failed_checks=[],
            all_checks=[],
        )

    if failed_checks:
        failure_summaries = [f"[{c.check_type}] {c.message}" for c in failed_checks]
        return RejectedInsight(
            insight_id=candidate.insight_id,
            title=candidate.title,
            claim=candidate.claim,
            insight_type=candidate.insight_type,
            rejection_reason="; ".join(failure_summaries),
            failed_checks=failed_checks,
            all_checks=all_checks,
        )

    # 5. Deterministic Confidence Calculation (Zero LLM involvement)
    sample_size = discovery.row_count if discovery else 0
    missing_pct = (
        discovery.missingness.overall_missing_percentage
        if discovery and discovery.missingness
        else 0.0
    )

    confidence = calculate_deterministic_confidence(
        verification_checks=all_checks,
        sample_size=sample_size,
        missing_percentage=missing_pct,
    )

    return VerifiedInsight(
        insight_id=candidate.insight_id,
        title=candidate.title,
        claim=candidate.claim,
        insight_type=candidate.insight_type,
        entities_involved=candidate.entities_involved,
        confidence_score=confidence,
        evidence=all_checks,
        business_impact=candidate.business_impact,
        recommended_action=candidate.recommended_action,
        chart_recommendation=candidate.chart_recommendation,
    )


def verifier_node(state: AidaState) -> Dict[str, Any]:
    """LangGraph node executing the deterministic Trust Layer.

    Args:
        state: The current AidaState dictionary.

    Returns:
        Dictionary with state updates: verified_insights, rejected_insights, and insight_contract.
    """
    discovery = state.get("discovery_contract")
    analysis = state.get("analysis_contract")
    candidates = state.get("candidate_insights", [])
    critiques = state.get("critique_evaluations", [])
    errors = list(state.get("errors", []))

    critique_map = {c.insight_id: c for c in critiques}

    new_verified: List[VerifiedInsight] = []
    new_rejected: List[RejectedInsight] = []

    for candidate in candidates:
        try:
            critique = critique_map.get(candidate.insight_id)
            result = verify_single_candidate(
                candidate=candidate,
                discovery=discovery,
                analysis=analysis,
                critique=critique,
            )

            if isinstance(result, VerifiedInsight):
                new_verified.append(result)
            else:
                new_rejected.append(result)
        except Exception as exc:
            # Graceful failure isolation: never crash the pipeline
            error_msg = f"Unexpected error verifying candidate {candidate.insight_id}: {str(exc)}"
            errors.append(error_msg)
            new_rejected.append(
                RejectedInsight(
                    insight_id=candidate.insight_id,
                    title=candidate.title,
                    claim=candidate.claim,
                    insight_type=candidate.insight_type,
                    rejection_reason=f"Verification runtime error: {str(exc)}",
                    failed_checks=[],
                    all_checks=[],
                )
            )

    # Compile InsightContract for Person 4 (UI/Dashboard)
    dataset_id = discovery.dataset_id if discovery else (analysis.dataset_id if analysis else "unknown")
    mean_conf = (
        sum(v.confidence_score for v in new_verified) / len(new_verified)
        if new_verified
        else 0.0
    )

    contract = InsightContract(
        dataset_id=dataset_id,
        verified_insights=new_verified,
        rejected_insights=new_rejected,
        summary={
            "total_candidates": len(candidates),
            "verified_count": len(new_verified),
            "rejected_count": len(new_rejected),
            "verification_pass_rate": round(len(new_verified) / len(candidates), 3) if candidates else 0.0,
            "mean_confidence": round(mean_conf, 3),
        },
    )

    return {
        "verified_insights": new_verified,
        "rejected_insights": new_rejected,
        "insight_contract": contract,
        "errors": errors,
        "pipeline_errors": errors,
    }
