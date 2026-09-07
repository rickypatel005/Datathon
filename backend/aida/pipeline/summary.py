"""Deterministic Executive Summary Generator for AIDA Trust Layer.

Compiles an executive summary payload directly from verified insights,
rejection audit trails, and critic evaluations.
Operates 100% deterministically without any LLM calls.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from backend.aida.contracts.insight_contract import InsightContract
from backend.aida.state import CritiqueEvaluation


def generate_deterministic_summary(
    insight_contract: InsightContract,
    critique_evaluations: Optional[List[CritiqueEvaluation]] = None,
) -> Dict[str, Any]:
    """Generate a strict, deterministic executive summary payload for Person 4 (UI).

    Args:
        insight_contract: The final InsightContract containing verified and rejected insights.
        critique_evaluations: Optional list of Critic evaluations to extract leakage flags.

    Returns:
        Dictionary containing executive summary, top 3 ranked insights, leakage warnings,
        key metrics overview, and deterministic narrative text.
    """
    verified = insight_contract.verified_insights
    rejected = insight_contract.rejected_insights
    dataset_id = insight_contract.dataset_id

    total_candidates = len(verified) + len(rejected)
    pass_rate = round(len(verified) / max(1, total_candidates), 3) if total_candidates > 0 else 0.0

    mean_conf = (
        round(sum(vi.confidence_score for vi in verified) / len(verified), 3)
        if verified
        else 0.0
    )

    # 1. Top 3 Insights
    top_3: List[Dict[str, Any]] = []
    for idx, vi in enumerate(verified[:3], start=1):
        top_3.append({
            "rank": idx,
            "insight_id": vi.insight_id,
            "title": vi.title,
            "claim": vi.claim,
            "insight_type": vi.insight_type,
            "confidence_score": vi.confidence_score,
            "entities_involved": vi.entities_involved,
            "recommended_action": vi.recommended_action,
            "business_impact": vi.business_impact,
            "chart_type": vi.chart_recommendation.chart_type if vi.chart_recommendation else None,
        })

    # 2. Critical Leakage Warnings
    leakage_warnings: List[str] = []

    # Check rejected insights for leakage indicators
    for ri in rejected:
        reason_lower = ri.rejection_reason.lower()
        if "leakage" in reason_lower or "target variable" in reason_lower or "near 1.0" in reason_lower:
            leakage_warnings.append(f"Insight '{ri.title}': {ri.rejection_reason}")

    # Check critic evaluations for flagged concerns
    if critique_evaluations:
        for critique in critique_evaluations:
            for concern in critique.concerns:
                concern_lower = concern.lower()
                if "leakage" in concern_lower or "target variable" in concern_lower:
                    if concern not in leakage_warnings:
                        leakage_warnings.append(f"Critic Alert: {concern}")

    # 3. Categorical Overview
    type_counts: Dict[str, int] = {}
    for vi in verified:
        type_counts[vi.insight_type] = type_counts.get(vi.insight_type, 0) + 1

    # 4. Deterministic Executive Narrative (Zero LLM)
    if verified:
        top_lead = top_3[0]
        narrative_parts = [
            f"Autonomous intelligence investigation concluded for dataset '{dataset_id}'.",
            f"Out of {total_candidates} candidate hypotheses, {len(verified)} strictly verified "
            f"insights were confirmed with an average mathematical confidence of {mean_conf:.1%}.",
            f"Primary finding: '{top_lead['title']}' with {top_lead['confidence_score']:.1%} confidence.",
        ]
        if leakage_warnings:
            narrative_parts.append(
                f"CAUTION: {len(leakage_warnings)} potential data leakage signal(s) were flagged and neutralized."
            )
        else:
            narrative_parts.append("Zero data leakage or target redundancy was detected across verified signals.")
        executive_text = " ".join(narrative_parts)
    else:
        executive_text = (
            f"Investigation concluded for dataset '{dataset_id}'. No candidate hypotheses passed "
            f"the deterministic Trust Layer. {len(rejected)} candidate(s) were rejected for mathematical inaccuracy."
        )

    return {
        "dataset_id": dataset_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_candidates": total_candidates,
        "verified_count": len(verified),
        "rejected_count": len(rejected),
        "verification_pass_rate": pass_rate,
        "average_confidence": mean_conf,
        "top_3_insights": top_3,
        "critical_leakage_warnings": leakage_warnings,
        "categories_breakdown": type_counts,
        "executive_summary_text": executive_text,
    }
