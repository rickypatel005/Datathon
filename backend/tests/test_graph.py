"""End-to-End integration test for the compiled AIDA LangGraph pipeline."""

import pytest
from backend.aida.graph import aida_graph, create_aida_graph
from backend.aida.contracts.insight_contract import (
    InsightContract,
    VerifiedInsight,
    RejectedInsight,
    CandidateInsight,
)
from backend.aida.state import AidaState, CritiqueEvaluation
from backend.aida.mocks.mock_contracts import (
    get_mock_discovery_contract,
    get_mock_analysis_contract,
)


def test_aida_graph_end_to_end_execution():
    """Verify that mock contracts traverse Planner -> Investigator -> Critic -> Verifier -> END cleanly."""
    discovery = get_mock_discovery_contract()
    analysis = get_mock_analysis_contract()

    initial_state: AidaState = {
        "discovery_contract": discovery,
        "analysis_contract": analysis,
        "errors": [],
    }

    # Execute compiled LangGraph
    final_state = aida_graph.invoke(initial_state)

    # 1. Verify Planner Node Output
    assert "investigation_plan" in final_state
    plan = final_state["investigation_plan"]
    assert isinstance(plan, list)
    assert len(plan) > 0
    assert all(isinstance(item, str) for item in plan)

    # 2. Verify Investigator Node Output
    assert "candidate_insights" in final_state
    candidates = final_state["candidate_insights"]
    assert isinstance(candidates, list)
    assert len(candidates) > 0
    assert all(isinstance(c, CandidateInsight) for c in candidates)

    # 3. Verify Critic Node Output
    assert "critique_evaluations" in final_state
    critiques = final_state["critique_evaluations"]
    assert isinstance(critiques, list)
    assert len(critiques) == len(candidates)
    assert all(isinstance(cr, CritiqueEvaluation) for cr in critiques)

    # 4. Verify Verifier Node Output (The Trust Layer)
    assert "verified_insights" in final_state
    assert "rejected_insights" in final_state
    verified = final_state["verified_insights"]
    rejected = final_state["rejected_insights"]

    assert isinstance(verified, list)
    assert isinstance(rejected, list)
    assert len(verified) + len(rejected) == len(candidates)

    for vi in verified:
        assert isinstance(vi, VerifiedInsight)
        assert vi.status == "VERIFIED"
        assert 0.0 < vi.confidence_score <= 1.0
        assert len(vi.evidence) > 0
        assert all(check.passed for check in vi.evidence)

    for ri in rejected:
        assert isinstance(ri, RejectedInsight)
        assert ri.status == "REJECTED"
        assert len(ri.rejection_reason) > 0

    # 5. Verify Final Contract Output for Person 4 (UI/Dashboard)
    assert "insight_contract" in final_state
    contract: InsightContract = final_state["insight_contract"]
    assert isinstance(contract, InsightContract)
    assert contract.dataset_id == discovery.dataset_id
    assert contract.summary["total_candidates"] == len(candidates)
    assert contract.summary["verified_count"] == len(verified)
    assert contract.summary["rejected_count"] == len(rejected)


def test_create_fresh_graph_instance():
    """Verify that graph factory creates a distinct, executable graph."""
    graph = create_aida_graph()
    assert graph is not None

    discovery = get_mock_discovery_contract()
    analysis = get_mock_analysis_contract()

    result = graph.invoke({
        "discovery_contract": discovery,
        "analysis_contract": analysis,
    })

    assert "insight_contract" in result
    assert result["insight_contract"] is not None
