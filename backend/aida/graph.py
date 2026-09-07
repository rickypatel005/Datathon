"""AIDA End-to-End Insight Brain LangGraph Definition.

Wires the sequential 5-node pipeline:
    START -> Planner -> Investigator -> Critic -> Verifier -> Ranker -> END

Includes robust try/except error boundaries on each node and an execution runner
that ensures Person 4 (UI/Dashboard) always receives a valid InsightContract even
if catastrophic upstream failures occur.
"""

from __future__ import annotations
import logging
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timezone

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from backend.aida.state import AidaState
from backend.aida.agents.planner_node import planner_node
from backend.aida.agents.investigator_node import investigator_node
from backend.aida.agents.critic_node import critic_node
from backend.aida.verifier.verifier_node import verifier_node
from backend.aida.pipeline.insight_ranking import ranker_node
from backend.aida.contracts.insight_contract import InsightContract

logger = logging.getLogger(__name__)


def _make_resilient_node(node_fn: Callable[[AidaState], Dict[str, Any]], node_name: str) -> Callable[[AidaState], Dict[str, Any]]:
    """Wrap a LangGraph node function in a resilient try/except boundary.

    Prevents any uncaught node exception from crashing the pipeline graph.
    """
    def resilient_wrapper(state: AidaState) -> Dict[str, Any]:
        try:
            return node_fn(state)
        except Exception as exc:
            logger.exception("Error executing node '%s': %s", node_name, exc)
            errors = list(state.get("pipeline_errors", state.get("errors", [])))
            err_entry = f"[{node_name}] Resilient catch: {str(exc)}"
            errors.append(err_entry)

            fallback: Dict[str, Any] = {
                "pipeline_errors": errors,
                "errors": errors,
            }

            # Provide safe defaults based on which node crashed
            if node_name == "planner":
                fallback["investigation_plan"] = ["Fallback automated feature profiling"]
            elif node_name == "investigator":
                fallback["candidate_insights"] = []
            elif node_name == "critic":
                fallback["critique_evaluations"] = []
            elif node_name == "verifier":
                fallback["verified_insights"] = []
                fallback["rejected_insights"] = []
            elif node_name == "ranker":
                fallback["ranked_insights"] = []

            return fallback

    resilient_wrapper.__name__ = f"resilient_{node_name}"
    return resilient_wrapper


def create_aida_graph() -> CompiledStateGraph:
    """Build and compile the AIDA insight graph.

    Graph Topology:
        START -> planner -> investigator -> critic -> verifier -> ranker -> END
    """
    workflow = StateGraph(AidaState)

    # 1. Register Resilient Nodes
    workflow.add_node("planner", _make_resilient_node(planner_node, "planner"))
    workflow.add_node("investigator", _make_resilient_node(investigator_node, "investigator"))
    workflow.add_node("critic", _make_resilient_node(critic_node, "critic"))
    workflow.add_node("verifier", _make_resilient_node(verifier_node, "verifier"))
    workflow.add_node("ranker", _make_resilient_node(ranker_node, "ranker"))

    # 2. Add Sequential Edges
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "investigator")
    workflow.add_edge("investigator", "critic")
    workflow.add_edge("critic", "verifier")
    workflow.add_edge("verifier", "ranker")
    workflow.add_edge("ranker", END)

    # 3. Compile
    return workflow.compile()


# Default compiled graph instance
aida_graph: CompiledStateGraph = create_aida_graph()


def run_aida_pipeline(initial_state: AidaState | Dict[str, Any]) -> AidaState:
    """Execute the full AIDA pipeline with guaranteed contract generation.

    Ensures that Person 4 (UI) always receives a valid, non-null InsightContract,
    populating 'pipeline_errors' if failures occurred rather than throwing a 500 error.

    Args:
        initial_state: Initial state dictionary containing discovery and analysis contracts.

    Returns:
        Final state dictionary containing the verified InsightContract.
    """
    state_dict = dict(initial_state)
    errors = list(state_dict.get("pipeline_errors", state_dict.get("errors", [])))

    # Identify dataset ID safely
    dataset_id = "unknown_dataset"
    if "discovery_contract" in state_dict and state_dict["discovery_contract"]:
        dataset_id = getattr(state_dict["discovery_contract"], "dataset_id", "unknown_dataset")
    elif "analysis_contract" in state_dict and state_dict["analysis_contract"]:
        dataset_id = getattr(state_dict["analysis_contract"], "dataset_id", "unknown_dataset")

    try:
        final_state = aida_graph.invoke(state_dict)

        # Ensure insight_contract exists and pipeline_errors are propagated
        contract = final_state.get("insight_contract")
        if contract is None:
            final_state["insight_contract"] = InsightContract(
                dataset_id=dataset_id,
                verified_insights=final_state.get("verified_insights", []),
                rejected_insights=final_state.get("rejected_insights", []),
                summary={
                    "status": "COMPLETED_EMPTY",
                    "total_candidates": 0,
                    "verified_count": 0,
                    "rejected_count": 0,
                    "pipeline_errors": final_state.get("pipeline_errors", []),
                },
            )
        else:
            if final_state.get("pipeline_errors"):
                contract.summary["pipeline_errors"] = final_state.get("pipeline_errors", [])
        return final_state

    except Exception as exc:
        logger.exception("Catastrophic pipeline execution error: %s", exc)
        errors.append(f"Catastrophic pipeline error: {str(exc)}")

        fallback_contract = InsightContract(
            dataset_id=dataset_id,
            verified_insights=[],
            rejected_insights=[],
            summary={
                "status": "FAILED",
                "total_candidates": 0,
                "verified_count": 0,
                "rejected_count": 0,
                "error": str(exc),
                "pipeline_errors": errors,
                "executive_summary": {
                    "dataset_id": dataset_id,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "total_candidates": 0,
                    "verified_count": 0,
                    "rejected_count": 0,
                    "critical_leakage_warnings": [],
                    "executive_summary_text": f"Autonomous analysis halted gracefully: {str(exc)}",
                },
            },
        )

        return {
            "discovery_contract": state_dict.get("discovery_contract"),
            "analysis_contract": state_dict.get("analysis_contract"),
            "investigation_plan": [],
            "candidate_insights": [],
            "critique_evaluations": [],
            "verified_insights": [],
            "rejected_insights": [],
            "ranked_insights": [],
            "executive_summary": fallback_contract.summary.get("executive_summary"),
            "insight_contract": fallback_contract,
            "errors": errors,
            "pipeline_errors": errors,
        }
