"""Deterministic Insight Ranking Engine.

Ranks verified insights based on a mathematical composite score combining:
1. Confidence score (deterministic certainty).
2. Statistical support (empirical evidence density and tolerance precision).
3. Champion model alignment (relevance to top features of the best-performing model).
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from backend.aida.contracts.insight_contract import VerifiedInsight, InsightContract
from backend.aida.contracts.analysis_contract import AnalysisContract
from backend.aida.state import AidaState


def _calculate_statistical_support(insight: VerifiedInsight) -> float:
    """Calculate empirical statistical support score [0.0 - 1.0]."""
    if not insight.evidence:
        return 0.10

    # 1. Base pass rate across all checks
    passed_count = sum(1 for ev in insight.evidence if ev.passed)
    pass_rate = passed_count / len(insight.evidence)

    # 2. Evidence depth factor (1 check = 0.70, 2+ checks = 1.0)
    depth_factor = min(1.0, 0.40 + 0.30 * len(insight.evidence))

    # 3. Precision bonus for tight numerical tolerances
    precision_bonus = 0.0
    for ev in insight.evidence:
        if ev.tolerance <= 0.005:
            precision_bonus = 0.15
            break
        elif ev.tolerance <= 0.01:
            precision_bonus = 0.10

    raw_support = (pass_rate * 0.70 + depth_factor * 0.30) + precision_bonus
    return round(max(0.0, min(1.0, raw_support)), 3)


def _calculate_champion_alignment(
    insight: VerifiedInsight, champion_feature_importances: Dict[str, float]
) -> float:
    """Calculate feature alignment with champion model [0.0 - 1.0]."""
    if not champion_feature_importances or not insight.entities_involved:
        return 0.0

    normalized_map = {k.lower(): float(v) for k, v in champion_feature_importances.items()}

    matched_importances = []
    for entity in insight.entities_involved:
        ent_lower = entity.lower()
        if ent_lower in normalized_map:
            matched_importances.append(normalized_map[ent_lower])

    if not matched_importances:
        return 0.0

    # Scale max matched importance (features usually range 0.05 to 0.50+)
    max_matched = max(matched_importances)
    alignment_score = min(1.0, max_matched * 2.0)
    return round(alignment_score, 3)


def compute_composite_score(
    insight: VerifiedInsight, champion_feature_importances: Dict[str, float]
) -> float:
    """Compute the deterministic composite score used for ranking."""
    confidence = insight.confidence_score
    support = _calculate_statistical_support(insight)
    alignment = _calculate_champion_alignment(insight, champion_feature_importances)

    # Composite weighting: 40% Confidence, 35% Statistical Support, 25% Champion Alignment
    composite = (0.40 * confidence) + (0.35 * support) + (0.25 * alignment)
    return round(max(0.0, min(1.0, composite)), 4)


def rank_insights(
    verified_insights: List[VerifiedInsight],
    analysis_contract: Optional[AnalysisContract] = None,
) -> List[VerifiedInsight]:
    """Deterministically rank verified insights in descending order of composite score.

    Args:
        verified_insights: List of VerifiedInsight objects.
        analysis_contract: Optional AnalysisContract containing trained models and feature importances.

    Returns:
        Sorted list of VerifiedInsight objects (highest composite score first).
    """
    if not verified_insights:
        return []

    # Extract champion model feature importances if available
    champion_importances: Dict[str, float] = {}
    if analysis_contract:
        # Prefer best model by accuracy or f1; fallback to first model
        best_model = (
            analysis_contract.get_best_model(metric="accuracy")
            or analysis_contract.get_best_model(metric="f1")
            or (analysis_contract.models[0] if analysis_contract.models else None)
        )
        if best_model and best_model.feature_importances:
            champion_importances = best_model.feature_importances

    # Sort deterministically using composite score with title as secondary tie-breaker
    return sorted(
        verified_insights,
        key=lambda vi: (
            compute_composite_score(vi, champion_importances),
            vi.confidence_score,
            vi.title,
        ),
        reverse=True,
    )


def ranker_node(state: AidaState) -> Dict[str, Any]:
    """LangGraph node executing deterministic ranking on verified insights.

    Args:
        state: Current AidaState.

    Returns:
        State update dictionary containing ranked 'verified_insights',
        'ranked_insights', 'executive_summary', and updated 'insight_contract'.
    """
    from backend.aida.pipeline.summary import generate_deterministic_summary

    verified = state.get("verified_insights", [])
    analysis = state.get("analysis_contract")
    contract = state.get("insight_contract")
    critiques = state.get("critique_evaluations", [])
    errors = list(state.get("pipeline_errors", state.get("errors", [])))

    try:
        ranked_insights = rank_insights(verified, analysis_contract=analysis)
    except Exception as exc:
        errors.append(f"Ranking error: {str(exc)}")
        ranked_insights = verified

    exec_summary: Optional[Dict[str, Any]] = None

    # Update contract if already present in state
    if contract is not None:
        contract.verified_insights = ranked_insights
        exec_summary = generate_deterministic_summary(contract, critique_evaluations=critiques)
        contract.summary["is_ranked"] = True
        contract.summary["executive_summary"] = exec_summary

    return {
        "verified_insights": ranked_insights,
        "ranked_insights": ranked_insights,
        "executive_summary": exec_summary,
        "insight_contract": contract,
        "pipeline_errors": errors,
        "errors": errors,
    }

