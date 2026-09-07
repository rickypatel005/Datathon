"""Unit tests for deterministic insight ranking, executive summary generator, and pipeline hardening."""

import pytest
from datetime import datetime, timezone

from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.analysis_contract import AnalysisContract, ModelSummary
from backend.aida.contracts.insight_contract import (
    VerifiedInsight,
    RejectedInsight,
    VerificationCheckResult,
    InsightContract,
    ChartRecommendation,
)
from backend.aida.pipeline.insight_ranking import (
    rank_insights,
    compute_composite_score,
)
from backend.aida.pipeline.summary import generate_deterministic_summary
from backend.aida.graph import run_aida_pipeline, create_aida_graph
from backend.aida.mocks.mock_contracts import (
    get_mock_discovery_contract,
    get_mock_analysis_contract,
)


@pytest.fixture
def mock_analysis() -> AnalysisContract:
    return AnalysisContract(
        dataset_id="test_ds",
        models=[
            ModelSummary(
                model_name="ChampionRF",
                algorithm="RandomForest",
                evaluation_metrics={"accuracy": 0.92, "f1": 0.91},
                feature_importances={
                    "high_impact_feature": 0.45,
                    "medium_impact_feature": 0.25,
                    "low_impact_feature": 0.10,
                },
            )
        ],
    )


def test_ranking_sorts_correctly_by_composite_score(mock_analysis):
    """Insight with high confidence and champion alignment must rank highest."""
    # Insight 1: High confidence (0.95), aligned with top feature
    insight_high = VerifiedInsight(
        insight_id="ins-1",
        title="High Priority Driver",
        claim="Claim about high impact feature.",
        insight_type="feature_importance",
        entities_involved=["high_impact_feature"],
        confidence_score=0.95,
        evidence=[
            VerificationCheckResult(
                check_type="metric_exactness",
                passed=True,
                claimed_value=0.45,
                verified_value=0.45,
                tolerance=0.001,
                evidence_source="analysis",
                message="Exact match",
            ),
            VerificationCheckResult(
                check_type="feature_importance_ranking",
                passed=True,
                claimed_value=["high_impact_feature"],
                verified_value=["high_impact_feature"],
                tolerance=0.0,
                evidence_source="analysis",
                message="Top ranking confirmed",
            ),
        ],
    )

    # Insight 2: Medium confidence (0.75), aligned with medium feature
    insight_med = VerifiedInsight(
        insight_id="ins-2",
        title="Medium Priority Correlation",
        claim="Claim about medium impact feature.",
        insight_type="correlation",
        entities_involved=["medium_impact_feature"],
        confidence_score=0.75,
        evidence=[
            VerificationCheckResult(
                check_type="metric_exactness",
                passed=True,
                claimed_value=0.55,
                verified_value=0.55,
                tolerance=0.01,
                evidence_source="discovery",
                message="Exact match",
            )
        ],
    )

    # Insight 3: Low confidence (0.60), unaligned feature
    insight_low = VerifiedInsight(
        insight_id="ins-3",
        title="Low Priority Noise",
        claim="Claim about unaligned feature.",
        insight_type="data_quality",
        entities_involved=["unaligned_feature"],
        confidence_score=0.60,
        evidence=[
            VerificationCheckResult(
                check_type="metric_exactness",
                passed=True,
                claimed_value=1.0,
                verified_value=1.0,
                tolerance=0.05,
                evidence_source="discovery",
                message="Match with wide tolerance",
            )
        ],
    )

    # Input in reverse order: [low, med, high]
    ranked = rank_insights([insight_low, insight_med, insight_high], analysis_contract=mock_analysis)

    # Verification: Must sort strictly high -> med -> low
    assert [vi.insight_id for vi in ranked] == ["ins-1", "ins-2", "ins-3"]

    # Assert composite scores align
    champ_importances = mock_analysis.models[0].feature_importances
    score_high = compute_composite_score(insight_high, champ_importances)
    score_med = compute_composite_score(insight_med, champ_importances)
    score_low = compute_composite_score(insight_low, champ_importances)

    assert score_high > score_med > score_low


def test_ranking_handles_none_analysis_contract():
    """Ranking must function gracefully when no AnalysisContract is provided."""
    insight_a = VerifiedInsight(
        insight_id="ins-a",
        title="Strong Signal",
        claim="Good claim",
        insight_type="correlation",
        confidence_score=0.88,
        evidence=[
            VerificationCheckResult(
                check_type="metric_exactness",
                passed=True,
                claimed_value=0.5,
                verified_value=0.5,
                tolerance=0.001,
                evidence_source="discovery",
                message="Passed",
            )
        ],
    )
    insight_b = VerifiedInsight(
        insight_id="ins-b",
        title="Weak Signal",
        claim="Weak claim",
        insight_type="trend",
        confidence_score=0.62,
        evidence=[],
    )

    ranked = rank_insights([insight_b, insight_a], analysis_contract=None)
    assert ranked[0].insight_id == "ins-a"
    assert ranked[1].insight_id == "ins-b"


def test_deterministic_summary_generation_without_llm():
    """Summary generator must compile executive metrics and warnings deterministically."""
    verified_sample = [
        VerifiedInsight(
            insight_id="vi-1",
            title="Revenue Correlates with User Sessions",
            claim="Linear relationship of 0.78 between revenue and sessions.",
            insight_type="correlation",
            entities_involved=["revenue", "sessions"],
            confidence_score=0.92,
            evidence=[],
            recommended_action="Focus marketing on session duration.",
            chart_recommendation=ChartRecommendation(
                chart_type="scatter",
                title="Revenue vs Sessions",
            ),
        )
    ]

    rejected_sample = [
        RejectedInsight(
            insight_id="ri-1",
            title="Target Prediction Leakage",
            claim="Feature target_flag correlates perfectly with label.",
            insight_type="correlation",
            rejection_reason="Direct target leakage detected: feature is identical to target.",
            failed_checks=[],
        )
    ]

    contract = InsightContract(
        dataset_id="finance_q3",
        verified_insights=verified_sample,
        rejected_insights=rejected_sample,
    )

    summary = generate_deterministic_summary(contract)

    # 1. Structural assertions
    assert summary["dataset_id"] == "finance_q3"
    assert summary["verified_count"] == 1
    assert summary["rejected_count"] == 1
    assert summary["verification_pass_rate"] == 0.5
    assert summary["average_confidence"] == 0.92

    # 2. Top insights
    assert len(summary["top_3_insights"]) == 1
    top = summary["top_3_insights"][0]
    assert top["title"] == "Revenue Correlates with User Sessions"
    assert top["chart_type"] == "scatter"

    # 3. Leakage warnings
    assert len(summary["critical_leakage_warnings"]) == 1
    assert "target leakage" in summary["critical_leakage_warnings"][0].lower()

    # 4. Executive narrative text
    narrative = summary["executive_summary_text"]
    assert "finance_q3" in narrative
    assert "CAUTION" in narrative
    assert "92.0% confidence" in narrative


def test_full_pipeline_runner_and_summary_end_to_end():
    """run_aida_pipeline must successfully execute all 5 nodes and populate executive summary."""
    discovery = get_mock_discovery_contract()
    analysis = get_mock_analysis_contract()

    initial_state = {
        "discovery_contract": discovery,
        "analysis_contract": analysis,
    }

    final_state = run_aida_pipeline(initial_state)

    assert "ranked_insights" in final_state
    assert len(final_state["ranked_insights"]) > 0

    contract: InsightContract = final_state["insight_contract"]
    assert contract is not None
    assert contract.summary["is_ranked"] is True

    # Check executive summary in contract
    exec_summary = contract.summary.get("executive_summary")
    assert exec_summary is not None
    assert exec_summary["dataset_id"] == discovery.dataset_id
    assert len(exec_summary["top_3_insights"]) > 0
    assert "executive_summary_text" in exec_summary


def test_graceful_fallback_on_corrupted_inputs():
    """Pipeline runner must return a valid InsightContract with pipeline_errors if inputs are invalid."""
    # Pass empty dictionary without contracts
    corrupted_state = {}

    result = run_aida_pipeline(corrupted_state)

    assert "insight_contract" in result
    contract: InsightContract = result["insight_contract"]
    assert isinstance(contract, InsightContract)
    assert len(contract.verified_insights) == 0
    assert "pipeline_errors" in contract.summary or "error" in contract.summary
