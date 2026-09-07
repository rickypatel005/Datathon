"""Synthetic, dataset-agnostic mock contracts for Phase 0/1 development.

Provides realistic Discovery Contract (Person 1), Analysis Contract (Person 2),
and Candidate Insights to validate the Trust Layer prior to live pipeline integration.
"""

from typing import List
from backend.aida.contracts.discovery_contract import (
    DiscoveryContract,
    ColumnProfile,
    DistributionStats,
    CorrelationMatrix,
    MissingnessReport,
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
    ChartRecommendation,
)


def get_mock_discovery_contract() -> DiscoveryContract:
    """Realistic Discovery Contract from Person 1 for a customer analytics dataset."""
    return DiscoveryContract(
        dataset_id="ds_customer_churn_001",
        dataset_name="customer_churn_telemetry.csv",
        row_count=1250,
        column_count=6,
        columns={
            "session_duration": ColumnProfile(
                name="session_duration",
                semantic_type="numeric",
                raw_dtype="float64",
                null_count=0,
                null_percentage=0.0,
                unique_count=840,
                cardinality_ratio=0.672,
                distribution=DistributionStats(
                    count=1250,
                    mean=42.50,
                    std=12.10,
                    min=5.20,
                    q25=34.10,
                    median=41.80,
                    q75=50.20,
                    max=94.60,
                    skewness=0.35,
                    kurtosis=-0.12,
                ),
            ),
            "monthly_charges": ColumnProfile(
                name="monthly_charges",
                semantic_type="numeric",
                raw_dtype="float64",
                null_count=15,
                null_percentage=1.2,
                unique_count=610,
                cardinality_ratio=0.488,
                distribution=DistributionStats(
                    count=1235,
                    mean=64.80,
                    std=30.20,
                    min=18.50,
                    q25=38.40,
                    median=65.10,
                    q75=89.30,
                    max=118.90,
                    skewness=0.11,
                    kurtosis=-1.05,
                ),
            ),
            "support_tickets": ColumnProfile(
                name="support_tickets",
                semantic_type="numeric",
                raw_dtype="int64",
                null_count=0,
                null_percentage=0.0,
                unique_count=8,
                cardinality_ratio=0.0064,
                distribution=DistributionStats(
                    count=1250,
                    mean=2.15,
                    std=1.62,
                    min=0.0,
                    q25=1.0,
                    median=2.0,
                    q75=3.0,
                    max=7.0,
                    skewness=0.74,
                    kurtosis=0.18,
                ),
            ),
            "contract_tier": ColumnProfile(
                name="contract_tier",
                semantic_type="categorical",
                raw_dtype="object",
                null_count=0,
                null_percentage=0.0,
                unique_count=3,
                cardinality_ratio=0.0024,
                top_categories={"standard": 620, "premium": 410, "enterprise": 220},
            ),
            "region": ColumnProfile(
                name="region",
                semantic_type="categorical",
                raw_dtype="object",
                null_count=5,
                null_percentage=0.4,
                unique_count=4,
                cardinality_ratio=0.0032,
                top_categories={"east": 450, "west": 380, "north": 260, "south": 155},
            ),
            "churn_flag": ColumnProfile(
                name="churn_flag",
                semantic_type="boolean",
                raw_dtype="int64",
                null_count=0,
                null_percentage=0.0,
                unique_count=2,
                cardinality_ratio=0.0016,
                top_categories={"0": 980, "1": 270},
            ),
        },
        correlations=CorrelationMatrix(
            method="pearson",
            matrix={
                "session_duration": {
                    "monthly_charges": 0.724,
                    "support_tickets": -0.482,
                },
                "monthly_charges": {
                    "session_duration": 0.724,
                    "support_tickets": -0.315,
                },
                "support_tickets": {
                    "session_duration": -0.482,
                    "monthly_charges": -0.315,
                },
            },
        ),
        missingness=MissingnessReport(
            total_missing_cells=20,
            overall_missing_percentage=0.27,
            columns_with_missing=["monthly_charges", "region"],
        ),
        metadata={"created_by": "person_1_discovery", "pipeline_version": "v1.0"},
    )


def get_mock_analysis_contract() -> AnalysisContract:
    """Realistic Analysis Contract from Person 2 with ML evaluation and tests."""
    return AnalysisContract(
        dataset_id="ds_customer_churn_001",
        target_column="churn_flag",
        models=[
            ModelSummary(
                model_name="RandomForestClassifier",
                algorithm="RandomForest",
                task_type="classification",
                evaluation_metrics={
                    "accuracy": 0.884,
                    "f1": 0.862,
                    "precision": 0.871,
                    "recall": 0.854,
                    "roc_auc": 0.932,
                },
                feature_importances={
                    "monthly_charges": 0.420,
                    "session_duration": 0.285,
                    "support_tickets": 0.175,
                    "contract_tier": 0.080,
                    "region": 0.040,
                },
            ),
            ModelSummary(
                model_name="LogisticRegression",
                algorithm="LogisticRegression",
                task_type="classification",
                evaluation_metrics={
                    "accuracy": 0.812,
                    "f1": 0.785,
                    "precision": 0.801,
                    "recall": 0.770,
                    "roc_auc": 0.865,
                },
                feature_importances={
                    "monthly_charges": 0.390,
                    "session_duration": 0.260,
                    "support_tickets": 0.210,
                    "contract_tier": 0.095,
                    "region": 0.045,
                },
            ),
        ],
        statistical_tests=[
            StatisticalTestResult(
                test_name="chi_square",
                variables=["contract_tier", "churn_flag"],
                statistic=38.45,
                p_value=0.0001,
                alpha=0.05,
                is_significant=True,
                interpretation="Statistically significant association between contract tier and churn rate.",
            ),
            StatisticalTestResult(
                test_name="two_sample_t_test",
                variables=["session_duration", "churn_flag"],
                statistic=5.21,
                p_value=0.00004,
                alpha=0.05,
                is_significant=True,
                interpretation="Session duration differs significantly between churned and active users.",
            ),
        ],
        clustering=ClusteringSummary(
            algorithm="KMeans",
            n_clusters=3,
            silhouette_score=0.624,
            cluster_sizes={"cluster_0": 580, "cluster_1": 430, "cluster_2": 240},
        ),
        anomalies=AnomalySummary(
            algorithm="IsolationForest",
            anomaly_count=42,
            anomaly_percentage=3.36,
            features_analyzed=["monthly_charges", "session_duration", "support_tickets"],
        ),
        metadata={"created_by": "person_2_analysis", "ml_suite_version": "v1.2"},
    )


def get_mock_candidate_insights() -> List[CandidateInsight]:
    """Generate a diverse batch of candidate insights:

    - Candidate 1 (Valid): Real correlation claim matching discovery matrix.
    - Candidate 2 (Valid): Real top feature importance claim matching Random Forest.
    - Candidate 3 (Invalid - Hallucinated metric): Claims accuracy is 0.96 (actually 0.884).
    - Candidate 4 (Invalid - Inverted correlation): Claims positive correlation where actual is negative (-0.482).
    """
    return [
        # 1. Valid Correlation Insight
        CandidateInsight(
            title="Strong Positive Correlation Between Monthly Charges and Session Duration",
            claim="Users with higher monthly charges exhibit systematically longer session durations with a strong correlation of 0.724.",
            insight_type="correlation",
            entities_involved=["session_duration", "monthly_charges"],
            metric_claims=[
                MetricClaim(
                    metric_name="correlation",
                    source_contract="discovery",
                    entity_path="correlations.matrix.session_duration.monthly_charges",
                    claimed_value=0.724,
                    claimed_direction="positive",
                    tolerance=0.01,
                )
            ],
            business_impact="Premium tier customers demonstrate high platform engagement, suggesting monetization and usage align well.",
            recommended_action="Introduce loyalty rewards for users exceeding 60 minutes of weekly session duration.",
            chart_recommendation=ChartRecommendation(
                chart_type="scatter",
                title="Monthly Charges vs. Session Duration",
                x_axis="monthly_charges",
                y_axis="session_duration",
                description="Scatter plot highlighting the strong positive linear relationship.",
            ),
        ),

        # 2. Valid Feature Importance Insight
        CandidateInsight(
            title="Monthly Charges is the Primary Predictive Driver of Churn",
            claim="Random Forest model analysis reveals that monthly charges is the top predictive feature with an importance weight of 0.420.",
            insight_type="feature_importance",
            entities_involved=["monthly_charges", "RandomForestClassifier"],
            metric_claims=[
                MetricClaim(
                    metric_name="feature_importance",
                    source_contract="analysis",
                    entity_path="models.RandomForestClassifier.feature_importances.monthly_charges",
                    claimed_value=0.420,
                    tolerance=0.01,
                )
            ],
            business_impact="Price sensitivity is the dominant mechanism driving customer retention outcomes.",
            recommended_action="Conduct targeted price elasticity experiments to optimize tier pricing thresholds.",
            chart_recommendation=ChartRecommendation(
                chart_type="bar",
                title="Feature Importance Ranking for Churn Prediction",
                x_axis="feature_importances",
                y_axis="features",
                description="Horizontal bar chart illustrating relative model feature weights.",
            ),
        ),

        # 3. Invalid Insight: Hallucinated Accuracy Metric
        CandidateInsight(
            title="Model Achieves Extraordinary 96% Classification Accuracy",
            claim="The Random Forest model attained 96.0% accuracy on the test partition.",
            insight_type="model_performance",
            entities_involved=["RandomForestClassifier"],
            metric_claims=[
                MetricClaim(
                    metric_name="accuracy",
                    source_contract="analysis",
                    entity_path="models.RandomForestClassifier.evaluation_metrics.accuracy",
                    claimed_value=0.960,  # Real value is 0.884! This must FAIL verification.
                    tolerance=0.005,
                )
            ],
            business_impact="Overstated capability risks operational failure if deployed under false performance assumptions.",
        ),

        # 4. Invalid Insight: Inverted Correlation Direction
        CandidateInsight(
            title="Support Tickets Correlate Positively with Session Duration",
            claim="Users opening more support tickets spend significantly longer in sessions (positive correlation of 0.65).",
            insight_type="correlation",
            entities_involved=["support_tickets", "session_duration"],
            metric_claims=[
                MetricClaim(
                    metric_name="correlation",
                    source_contract="discovery",
                    entity_path="correlations.matrix.session_duration.support_tickets",
                    claimed_value=0.650,  # Real value is -0.482! Must FAIL both direction & magnitude.
                    claimed_direction="positive",
                    tolerance=0.01,
                )
            ],
        ),
    ]
