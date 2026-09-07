"""Deterministic Mathematical Confidence Engine.

Enforces that confidence scores are NEVER invented, estimated, or tuned by LLMs.
Scores are derived purely from empirical sample size, statistical significance,
verification pass integrity, and data quality indicators.
"""

from __future__ import annotations
import math
from typing import List, Optional
from backend.aida.contracts.insight_contract import VerificationCheckResult


def calculate_deterministic_confidence(
    verification_checks: List[VerificationCheckResult],
    sample_size: int,
    missing_percentage: float = 0.0,
    p_value: Optional[float] = None,
    primary_metric_score: Optional[float] = None,
) -> float:
    """Calculate a mathematically grounded trust/confidence score [0.0 - 1.0].

    Zero LLM involvement. Deterministic function of:
    1. Verification integrity (all checks MUST pass).
    2. Sample size sufficiency (logarithmic scaling).
    3. Missingness penalty (data quality impact).
    4. Formal statistical significance (p-value if available).
    5. Underlying model performance (if insight stems from ML).

    Returns:
        float: Deterministic score between 0.0 and 0.99.
    """
    if not verification_checks:
        return 0.0

    # Rule 1: If any verification check failed, confidence is strictly 0.0
    if not all(check.passed for check in verification_checks):
        return 0.0

    # Base score for passing 100% of factual checks
    base_score = 0.85

    # 1. Sample Size Reliability
    # Diminishing returns scaling: log10 curve
    if sample_size <= 0:
        sample_adj = -0.40
    elif sample_size < 30:
        sample_adj = -0.30  # Dangerously low sample size (Student's t boundary)
    elif sample_size < 100:
        sample_adj = -0.15
    elif sample_size < 1000:
        sample_adj = -0.05
    elif sample_size >= 10000:
        sample_adj = +0.05
    else:
        sample_adj = 0.0

    # 2. Data Quality / Missingness Impact
    if missing_percentage > 30.0:
        missing_adj = -0.25
    elif missing_percentage > 15.0:
        missing_adj = -0.12
    elif missing_percentage > 5.0:
        missing_adj = -0.05
    elif missing_percentage == 0.0:
        missing_adj = +0.03
    else:
        missing_adj = 0.0

    # 3. Statistical Significance (Hypothesis test / p-value)
    p_value_adj = 0.0
    if p_value is not None:
        if p_value < 0.001:
            p_value_adj = +0.06
        elif p_value < 0.01:
            p_value_adj = +0.04
        elif p_value < 0.05:
            p_value_adj = +0.01
        else:
            # Failed significance threshold alpha = 0.05
            p_value_adj = -0.25

    # 4. Model Metric Grounding (e.g. test accuracy or F1)
    model_adj = 0.0
    if primary_metric_score is not None:
        # Scale between -0.10 and +0.05 based on model capability
        clamped_metric = max(0.0, min(1.0, primary_metric_score))
        model_adj = (clamped_metric - 0.75) * 0.20

    raw_score = base_score + sample_adj + missing_adj + p_value_adj + model_adj

    # Clamp strictly within [0.10, 0.99]
    return round(max(0.10, min(0.99, raw_score)), 3)
