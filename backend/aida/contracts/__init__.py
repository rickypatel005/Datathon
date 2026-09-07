"""Contract schemas for AIDA pipeline communication."""

from backend.aida.contracts.discovery_contract import (
    DiscoveryContract,
    ColumnProfile,
    DistributionStats,
)
from backend.aida.contracts.analysis_contract import (
    AnalysisContract,
    ModelSummary,
    StatisticalTestResult,
    ClusteringSummary,
    AnomalySummary,
)
from backend.aida.contracts.insight_contract import (
    CandidateInsight,
    MetricClaim,
    VerificationCheckResult,
    VerifiedInsight,
    RejectedInsight,
    InsightContract,
    ChartRecommendation,
)

__all__ = [
    "DiscoveryContract",
    "ColumnProfile",
    "DistributionStats",
    "AnalysisContract",
    "ModelSummary",
    "StatisticalTestResult",
    "ClusteringSummary",
    "AnomalySummary",
    "CandidateInsight",
    "MetricClaim",
    "VerificationCheckResult",
    "VerifiedInsight",
    "RejectedInsight",
    "InsightContract",
    "ChartRecommendation",
]
