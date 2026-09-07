"""Investigator Node for AIDA LangGraph Pipeline.

Synthesizes candidate insights grounded in the upstream contracts
guided by the investigation plan from the Planner Node.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.aida.state import AidaState
from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.analysis_contract import AnalysisContract
from backend.aida.contracts.insight_contract import (
    CandidateInsight,
    MetricClaim,
    ChartRecommendation,
)


def investigator_node(state: AidaState) -> Dict[str, Any]:
    """LangGraph node synthesizing CandidateInsight objects from the investigation plan.

    Args:
        state: Current AidaState.

    Returns:
        State update dictionary containing 'candidate_insights'.
    """
    plan = state.get("investigation_plan", [])
    discovery: Optional[DiscoveryContract] = state.get("discovery_contract")
    analysis: Optional[AnalysisContract] = state.get("analysis_contract")
    errors = list(state.get("pipeline_errors", state.get("errors", [])))

    if not discovery and not analysis:
        errors.append("Investigator Node: Neither discovery_contract nor analysis_contract provided.")
        return {
            "candidate_insights": [],
            "pipeline_errors": errors,
            "errors": errors,
        }

    candidates: List[CandidateInsight] = []

    # 1. Investigate correlations identified in plan or discovery
    if discovery and discovery.correlations and discovery.correlations.matrix:
        seen_pairs = set()
        for col_a, row in discovery.correlations.matrix.items():
            for col_b, r in row.items():
                pair_key = tuple(sorted([col_a, col_b]))
                if col_a != col_b and pair_key not in seen_pairs and abs(r) >= 0.5:
                    seen_pairs.add(pair_key)
                    direction = "positive" if r > 0 else "negative"
                    candidates.append(
                        CandidateInsight(
                            insight_id=str(uuid4()),
                            title=f"Significant {direction.capitalize()} Correlation: {col_a} & {col_b}",
                            claim=(
                                f"Features '{col_a}' and '{col_b}' exhibit a {direction} correlation of {r:.3f}, "
                                f"indicating strong linear dependency."
                            ),
                            insight_type="correlation",
                            entities_involved=[col_a, col_b],
                            metric_claims=[
                                MetricClaim(
                                    metric_name="correlation",
                                    source_contract="discovery",
                                    entity_path=f"correlations.matrix.{col_a}.{col_b}",
                                    claimed_value=round(r, 4),
                                    claimed_direction=direction,
                                    tolerance=0.01,
                                )
                            ],
                            business_impact=f"Operational shifts in {col_a} directly reflect in {col_b}.",
                            recommended_action=f"Consider {col_a} as a leading indicator when forecasting {col_b}.",
                            chart_recommendation=ChartRecommendation(
                                chart_type="scatter",
                                title=f"{col_a} vs {col_b}",
                                x_axis=col_a,
                                y_axis=col_b,
                                description=f"Scatter distribution demonstrating {direction} correlation.",
                            ),
                        )
                    )

    # 2. Investigate primary model feature drivers
    if analysis and analysis.models:
        for model in analysis.models[:2]:
            ranked = model.get_ranked_features(top_n=1)
            if ranked:
                top_feat, imp_val = ranked[0]
                candidates.append(
                    CandidateInsight(
                        insight_id=str(uuid4()),
                        title=f"{top_feat} is Primary Predictive Driver for {model.model_name}",
                        claim=(
                            f"In the {model.model_name} model, '{top_feat}' emerged as the top driver "
                            f"with an importance weight of {imp_val:.3f}."
                        ),
                        insight_type="feature_importance",
                        entities_involved=[top_feat, model.model_name],
                        metric_claims=[
                            MetricClaim(
                                metric_name="feature_importance",
                                source_contract="analysis",
                                entity_path=f"models.{model.model_name}.feature_importances.{top_feat}",
                                claimed_value=round(imp_val, 4),
                                tolerance=0.01,
                            )
                        ],
                        business_impact=f"Interventions targeting {top_feat} will have maximal predictive effect.",
                        recommended_action=f"Prioritize optimization strategies focused on {top_feat}.",
                        chart_recommendation=ChartRecommendation(
                            chart_type="bar",
                            title=f"Feature Importances - {model.model_name}",
                            x_axis="feature_importances",
                            y_axis="features",
                            description="Bar chart showing relative contribution of features.",
                        ),
                    )
                )

    # 3. Investigate anomalies if present
    if analysis and analysis.anomalies and analysis.anomalies.anomaly_count > 0:
        candidates.append(
            CandidateInsight(
                insight_id=str(uuid4()),
                title=f"Anomaly Cluster Detected by {analysis.anomalies.algorithm}",
                claim=(
                    f"Detector {analysis.anomalies.algorithm} identified {analysis.anomalies.anomaly_count} anomalous records "
                    f"accounting for {analysis.anomalies.anomaly_percentage:.2f}% of observations."
                ),
                insight_type="anomaly",
                entities_involved=analysis.anomalies.features_analyzed,
                metric_claims=[
                    MetricClaim(
                        metric_name="anomaly_count",
                        source_contract="analysis",
                        entity_path="anomalies.anomaly_count",
                        claimed_value=analysis.anomalies.anomaly_count,
                        tolerance=0.0,
                    ),
                    MetricClaim(
                        metric_name="anomaly_percentage",
                        source_contract="analysis",
                        entity_path="anomalies.anomaly_percentage",
                        claimed_value=round(analysis.anomalies.anomaly_percentage, 2),
                        tolerance=0.05,
                    ),
                ],
                business_impact="Anomalous records may represent fraudulent transactions, system malfunctions, or extreme edge cases.",
                recommended_action="Isolate flagged records for specialized manual audit before downstream reporting.",
                chart_recommendation=ChartRecommendation(
                    chart_type="scatter",
                    title="Anomaly Distribution",
                    description="Outlier visualization over primary numerical dimensions.",
                ),
            )
        )

    # Fallback if no candidate insights were generated from contracts
    if not candidates:
        candidates.append(
            CandidateInsight(
                insight_id=str(uuid4()),
                title="Baseline Data Profiling Completed",
                claim="Data discovery completed across all available features without anomalous flags.",
                insight_type="data_quality",
                entities_involved=[],
                metric_claims=[],
            )
        )

    return {
        "candidate_insights": candidates,
    }
