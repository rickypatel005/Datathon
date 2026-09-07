"""Insight Contract Schema (Output to Person 4 - UI/Dashboard).

The Trust Layer's final deliverable: strictly verified insights with deterministic
evidence, mathematical confidence scores, visualization recommendations,
and a comprehensive audit trail of rejected insights.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class MetricClaim(BaseModel):
    """An explicit quantitative or structural claim made in an insight."""
    model_config = ConfigDict(extra="ignore")

    metric_name: str = Field(..., description="e.g. 'mean', 'correlation', 'accuracy', 'feature_importance'")
    source_contract: Literal["discovery", "analysis"] = Field(
        ..., description="Which upstream contract holds the ground truth"
    )
    entity_path: str = Field(
        ...,
        description="JSON path or dot-separated identifier pointing to ground truth, "
                    "e.g. 'columns.col_a.distribution.mean' or 'models.RandomForest.metrics.accuracy'",
    )
    claimed_value: Any = Field(..., description="The exact value asserted in the insight")
    claimed_direction: Optional[Literal["positive", "negative", "neutral"]] = Field(
        None, description="Claimed direction for trends/correlations"
    )
    tolerance: float = Field(
        default=1e-3, ge=0.0, description="Acceptable floating point rounding difference"
    )


class ChartRecommendation(BaseModel):
    """Visualization suggestion for the UI (Person 4)."""
    model_config = ConfigDict(extra="ignore")

    chart_type: Literal["bar", "line", "scatter", "box", "heatmap", "donut", "histogram"] = Field(
        ..., description="Recommended chart type"
    )
    title: str = Field(..., description="User-friendly title for the chart")
    x_axis: Optional[str] = Field(None, description="Column name for x-axis")
    y_axis: Optional[str] = Field(None, description="Column name for y-axis")
    color_by: Optional[str] = Field(None, description="Optional category column to segment/color by")
    description: Optional[str] = Field(None, description="Guidance on what this visualization illustrates")


class CandidateInsight(BaseModel):
    """Insight proposed by Investigator Node, pending Critic and Verifier checks."""
    model_config = ConfigDict(extra="ignore")

    insight_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="Punchy, actionable summary title")
    claim: str = Field(..., description="Detailed textual claim grounding the insight")
    insight_type: Literal[
        "trend", "correlation", "anomaly", "feature_importance", "model_performance", "data_quality", "distribution"
    ] = Field(..., description="Taxonomy of the insight")
    entities_involved: List[str] = Field(
        default_factory=list, description="Columns, features, or model names referenced"
    )
    metric_claims: List[MetricClaim] = Field(
        default_factory=list, description="All numerical/factual assertions required to be verified"
    )
    business_impact: Optional[str] = Field(None, description="Actionable business or operational consequence")
    recommended_action: Optional[str] = Field(None, description="Suggested next action or decision")
    chart_recommendation: Optional[ChartRecommendation] = Field(None, description="Suggested visualization")


class VerificationCheckResult(BaseModel):
    """Result of an individual deterministic check against the ground truth contracts."""
    model_config = ConfigDict(extra="ignore")

    check_id: str = Field(default_factory=lambda: str(uuid4()))
    check_type: Literal[
        "metric_exactness", "correlation_validity", "feature_importance_ranking", "model_agreement", "statistical_significance"
    ] = Field(..., description="Category of deterministic verification executed")
    passed: bool = Field(..., description="True if claimed value matched ground truth within tolerance")
    claimed_value: Any = Field(..., description="Value asserted in the insight")
    verified_value: Any = Field(..., description="Actual value retrieved deterministically from contract")
    tolerance: float = Field(default=1e-3, description="Tolerance applied during evaluation")
    evidence_source: str = Field(..., description="Path/pointer in contract confirming verification")
    message: str = Field(..., description="Detailed verification result statement")
    error_detail: Optional[str] = Field(None, description="Diagnostic error if verification failed")


class VerifiedInsight(BaseModel):
    """Fully verified, trust-guaranteed insight sent to Person 4 (Dashboard/UI)."""
    model_config = ConfigDict(extra="ignore")

    insight_id: str
    status: Literal["VERIFIED"] = "VERIFIED"
    title: str
    claim: str
    insight_type: str
    entities_involved: List[str] = Field(default_factory=list)
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="DETERMINISTIC confidence calculated mathematically. Never generated by LLM."
    )
    verified_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    evidence: List[VerificationCheckResult] = Field(
        ..., description="Complete proof chain from deterministic verification functions"
    )
    business_impact: Optional[str] = None
    recommended_action: Optional[str] = None
    chart_recommendation: Optional[ChartRecommendation] = None


class RejectedInsight(BaseModel):
    """Auditable log of candidate insights rejected by the Verifier Node."""
    model_config = ConfigDict(extra="ignore")

    insight_id: str
    status: Literal["REJECTED"] = "REJECTED"
    title: str
    claim: str
    insight_type: str
    rejected_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    rejection_reason: str = Field(..., description="Root cause explanation for rejection")
    failed_checks: List[VerificationCheckResult] = Field(
        ..., description="Deterministic checks that failed verification"
    )
    all_checks: List[VerificationCheckResult] = Field(
        default_factory=list, description="All checks executed on this candidate"
    )


class InsightContract(BaseModel):
    """Final output payload delivered to Person 4 (UI / Visualization layer)."""
    model_config = ConfigDict(extra="ignore")

    dataset_id: str = Field(..., description="Dataset analyzed")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    verified_insights: List[VerifiedInsight] = Field(
        default_factory=list, description="Verified insights with guaranteed mathematical grounding"
    )
    rejected_insights: List[RejectedInsight] = Field(
        default_factory=list, description="Audit log of rejected candidate insights"
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict, description="Aggregated execution metrics and trust score stats"
    )
