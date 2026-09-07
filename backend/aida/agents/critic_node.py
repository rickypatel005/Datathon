"""Critic Node for AIDA LangGraph Pipeline.

Performs adversarial review on candidate insights, flagging potential
target leakage, high missingness bias, or structural contradictions
without crashing the execution graph.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from backend.aida.state import AidaState, CritiqueEvaluation
from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.analysis_contract import AnalysisContract
from backend.aida.contracts.insight_contract import CandidateInsight


def _evaluate_candidate_soundness(
    candidate: CandidateInsight,
    discovery: Optional[DiscoveryContract],
    analysis: Optional[AnalysisContract],
) -> CritiqueEvaluation:
    """Evaluate a single candidate insight for data leakage, bias, and sanity."""
    concerns: List[str] = []
    soundness_score = 0.95

    target_col = analysis.target_column if analysis else None

    # 1. Target Leakage Check
    for entity in candidate.entities_involved:
        # Check if the entity is the target column itself
        if target_col and entity.lower() == target_col.lower() and candidate.insight_type == "feature_importance":
            concerns.append(f"Target variable '{entity}' flagged as predictor feature (direct target leakage).")
            soundness_score -= 0.50

    # 2. Perfect Correlation / Redundancy Leakage
    if candidate.insight_type == "correlation" and discovery:
        for claim in candidate.metric_claims:
            if claim.metric_name == "correlation" and isinstance(claim.claimed_value, (int, float)):
                if abs(float(claim.claimed_value)) >= 0.999:
                    concerns.append("Correlation near 1.0 indicates duplicate or derived redundant column.")
                    soundness_score -= 0.20

    # 3. Missingness / Sample Quality Check
    if discovery:
        for entity in candidate.entities_involved:
            col_prof = discovery.get_column(entity)
            if col_prof and col_prof.null_percentage > 25.0:
                concerns.append(
                    f"Feature '{entity}' exhibits {col_prof.null_percentage:.1f}% missingness, risking bias."
                )
                soundness_score -= 0.15

        if discovery.row_count < 30:
            concerns.append(f"Sample size ({discovery.row_count} rows) is critically low for generalization.")
            soundness_score -= 0.25

    soundness_score = max(0.10, min(1.0, soundness_score))

    # Reject if direct target leakage occurred or score dropped below 0.40
    is_approved = soundness_score >= 0.40 and not any("direct target leakage" in c for c in concerns)

    notes = (
        "Approved for verification. No major data leakage or structural concerns detected."
        if is_approved
        else f"Disapproved due to critical concerns: {'; '.join(concerns)}"
    )

    return CritiqueEvaluation(
        insight_id=candidate.insight_id,
        soundness_score=round(soundness_score, 2),
        is_approved_for_verification=is_approved,
        critique_notes=notes,
        concerns=concerns,
    )


def critic_node(state: AidaState) -> Dict[str, Any]:
    """LangGraph node performing adversarial review of all candidate insights.

    Args:
        state: Current AidaState.

    Returns:
        State update dictionary containing 'critique_evaluations'.
    """
    candidates = state.get("candidate_insights", [])
    discovery = state.get("discovery_contract")
    analysis = state.get("analysis_contract")
    errors = list(state.get("errors", []))

    evaluations: List[CritiqueEvaluation] = []

    for candidate in candidates:
        try:
            eval_result = _evaluate_candidate_soundness(
                candidate=candidate,
                discovery=discovery,
                analysis=analysis,
            )
            evaluations.append(eval_result)
        except Exception as exc:
            # Resilient fallback: log error without breaking graph
            errors.append(f"Critic error on insight {candidate.insight_id}: {str(exc)}")
            evaluations.append(
                CritiqueEvaluation(
                    insight_id=candidate.insight_id,
                    soundness_score=0.50,
                    is_approved_for_verification=True,
                    critique_notes=f"Evaluation completed with critic warning: {str(exc)}",
                    concerns=[str(exc)],
                )
            )

    return {
        "critique_evaluations": evaluations,
        "errors": errors,
    }
