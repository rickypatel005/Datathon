"""Planner Node for AIDA LangGraph Pipeline.

Formulates prioritized investigation plans from Discovery and Analysis contracts
using LangChain ChatPromptTemplate with guaranteed JSON list output and resilient fallback.
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate

from backend.aida.state import AidaState
from backend.aida.contracts.discovery_contract import DiscoveryContract
from backend.aida.contracts.analysis_contract import AnalysisContract

PLANNER_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Senior Quantitative Analyst & Investigation Planner for AIDA (Autonomous Intelligence & Data Analyst).\n"
            "Your role is to inspect the provided Discovery Contract (raw data profile) and Analysis Contract (ML metrics).\n"
            "Formulate 3 to 6 focused, high-impact investigation threads to guide the autonomous analysis.\n\n"
            "Rules:\n"
            "1. Dataset-agnostic: Dynamically adapt to whatever features exist without preconceived assumptions.\n"
            "2. Prioritize: Focus on high correlations (|r| >= 0.5), top predictive model features, anomalies, and statistically significant signals (p < 0.05).\n"
            "3. Zero hallucination: Base all focus areas strictly on the contracts.\n"
            "4. Output format: You MUST return ONLY a valid JSON array of strings. Do not add markdown formatting or extra text.\n\n"
            "Example output:\n"
            "[\n"
            '  "Investigate strong correlation between feature_a and feature_b to understand linear dependencies",\n'
            '  "Analyze primary feature importance drivers for model_x",\n'
            '  "Examine statistical association between feature_c and target_y"\n'
            "]",
        ),
        (
            "human",
            "Dataset Discovery Summary:\n{discovery_summary}\n\n"
            "ML Analysis Summary:\n{analysis_summary}\n\n"
            "Generate the prioritized investigation plan as a strict JSON list of strings.",
        ),
    ]
)


def _format_discovery_summary(contract: Optional[DiscoveryContract]) -> str:
    """Extract a concise, structural summary of the discovery contract."""
    if not contract:
        return "No discovery contract provided."

    summary = {
        "dataset_id": contract.dataset_id,
        "row_count": contract.row_count,
        "column_count": contract.column_count,
        "columns": [
            {
                "name": col.name,
                "type": col.semantic_type,
                "null_pct": col.null_percentage,
                "is_constant": col.is_constant,
            }
            for col in contract.columns.values()
        ],
        "top_correlations": [],
    }

    if contract.correlations and contract.correlations.matrix:
        seen = set()
        for col_a, row in contract.correlations.matrix.items():
            for col_b, r in row.items():
                if col_a != col_b and (col_b, col_a) not in seen:
                    seen.add((col_a, col_b))
                    if abs(r) >= 0.3:
                        summary["top_correlations"].append(
                            {"pair": [col_a, col_b], "r": round(r, 3)}
                        )

    return json.dumps(summary, indent=2)


def _format_analysis_summary(contract: Optional[AnalysisContract]) -> str:
    """Extract a concise, structural summary of the analysis contract."""
    if not contract:
        return "No analysis contract provided."

    summary = {
        "dataset_id": contract.dataset_id,
        "target_column": contract.target_column,
        "models": [
            {
                "name": m.model_name,
                "algorithm": m.algorithm,
                "metrics": m.evaluation_metrics,
                "top_features": m.get_ranked_features(top_n=3),
            }
            for m in contract.models
        ],
        "significant_tests": [
            {
                "test": t.test_name,
                "variables": t.variables,
                "p_value": t.p_value,
            }
            for t in contract.statistical_tests
            if t.is_significant
        ],
        "anomalies": contract.anomalies.model_dump() if contract.anomalies else None,
        "clustering": contract.clustering.model_dump() if contract.clustering else None,
    }

    return json.dumps(summary, indent=2)


def _generate_fallback_plan(
    discovery: Optional[DiscoveryContract], analysis: Optional[AnalysisContract]
) -> List[str]:
    """Deterministically synthesizes an investigation plan directly from contract contracts.

    Guarantees that Phase 0/1 offline testing and pipelines without LLM API keys
    never fail and always produce high-quality, dataset-agnostic investigation plans.
    """
    plan: List[str] = []

    # 1. Inspect correlations
    if discovery and discovery.correlations and discovery.correlations.matrix:
        for col_a, row in discovery.correlations.matrix.items():
            for col_b, r in row.items():
                if col_a < col_b and abs(r) >= 0.5:
                    direction = "positive" if r > 0 else "negative"
                    plan.append(
                        f"Investigate {direction} correlation between '{col_a}' and '{col_b}' (r={r:.3f})"
                    )

    # 2. Inspect ML models & top feature importances
    if analysis and analysis.models:
        best_model = analysis.get_best_model(metric="accuracy") or analysis.models[0]
        top_feats = best_model.get_ranked_features(top_n=2)
        if top_feats:
            feat_names = [f[0] for f in top_feats]
            plan.append(
                f"Analyze primary feature importance drivers for '{best_model.model_name}' ({', '.join(feat_names)})"
            )

    # 3. Inspect significant statistical tests
    if analysis and analysis.statistical_tests:
        for test in analysis.statistical_tests:
            if test.is_significant:
                plan.append(
                    f"Examine statistical relationship for {test.test_name} between {', '.join(test.variables)} (p={test.p_value:.4f})"
                )

    # 4. Inspect anomalies
    if analysis and analysis.anomalies and analysis.anomalies.anomaly_count > 0:
        plan.append(
            f"Evaluate {analysis.anomalies.anomaly_count} anomalies flagged by {analysis.anomalies.algorithm} ({analysis.anomalies.anomaly_percentage:.1f}% of dataset)"
        )

    # 5. Inspect missingness
    if discovery and discovery.missingness and discovery.missingness.columns_with_missing:
        cols = ", ".join(discovery.missingness.columns_with_missing[:3])
        plan.append(
            f"Audit missing data impact on feature integrity ({cols})"
        )

    # Ensure at least a generic investigation plan if contracts are empty
    if not plan:
        plan = [
            "Perform automated distribution and variance profiling across features",
            "Examine potential feature relationships and target predictability",
        ]

    return plan[:6]


def planner_node(state: AidaState, llm: Optional[Any] = None) -> Dict[str, Any]:
    """LangGraph node executing the investigation planning step.

    Args:
        state: The current AidaState dictionary.
        llm: Optional LangChain chat model. If None or if LLM call fails,
             uses the deterministic fallback generator.

    Returns:
        State update dictionary containing 'investigation_plan'.
    """
    discovery = state.get("discovery_contract")
    analysis = state.get("analysis_contract")

    plan: List[str] = []

    if llm is not None:
        try:
            discovery_summary = _format_discovery_summary(discovery)
            analysis_summary = _format_analysis_summary(analysis)

            prompt = PLANNER_PROMPT_TEMPLATE.format_messages(
                discovery_summary=discovery_summary,
                analysis_summary=analysis_summary,
            )
            response = llm.invoke(prompt)
            content = getattr(response, "content", str(response)).strip()

            # Attempt JSON extraction
            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
                    plan = parsed
        except Exception:
            # Fall back to deterministic generation on any error
            plan = []

    if not plan:
        plan = _generate_fallback_plan(discovery, analysis)

    return {
        "investigation_plan": plan,
    }
