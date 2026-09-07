"""
CrewAI Task definitions that map to the analysis pipeline.
"""
try:
    from crewai import Task
except (ImportError, Exception):
    class Task:
        def __init__(self, *args, **kwargs):
            self.description = kwargs.get("description", "")
            self.expected_output = kwargs.get("expected_output", "")
            self.agent = kwargs.get("agent", None)
from typing import Dict, Any


def create_dataset_understanding_task(agent, dataset_info: str) -> Task:
    return Task(
        description=(
            f"Analyze the following dataset and provide a comprehensive understanding:\n\n"
            f"{dataset_info}\n\n"
            "Your analysis should include:\n"
            "1. Overview of all columns with data types\n"
            "2. Identification of potential target variables\n"
            "3. Relationships between columns\n"
            "4. Data quality assessment\n"
            "5. Recommendations for further analysis"
        ),
        expected_output=(
            "A structured JSON report containing column metadata, data types, "
            "null percentages, unique counts, potential relationships, and analysis recommendations."
        ),
        agent=agent,
    )


def create_data_cleaning_task(agent, dataset_info: str, cleaning_report: str) -> Task:
    return Task(
        description=(
            f"Review the dataset cleaning results and provide recommendations:\n\n"
            f"Dataset Info:\n{dataset_info}\n\n"
            f"Cleaning Report:\n{cleaning_report}\n\n"
            "Evaluate the cleaning steps taken and suggest any additional "
            "transformations, feature engineering, or data quality improvements."
        ),
        expected_output=(
            "A detailed assessment of the cleaning process with recommendations "
            "for additional transformations or feature engineering steps."
        ),
        agent=agent,
    )


def create_eda_task(agent, dataset_info: str, eda_results: str) -> Task:
    return Task(
        description=(
            f"Analyze the following EDA results and provide statistical insights:\n\n"
            f"Dataset Info:\n{dataset_info}\n\n"
            f"EDA Results:\n{eda_results}\n\n"
            "Provide:\n"
            "1. Key statistical findings\n"
            "2. Notable correlations and their implications\n"
            "3. Distribution analysis insights\n"
            "4. Anomalies or interesting patterns\n"
            "5. Hypotheses for further investigation"
        ),
        expected_output=(
            "A comprehensive statistical analysis report with key findings, "
            "correlation insights, distribution patterns, and hypotheses."
        ),
        agent=agent,
    )


def create_visualization_task(agent, dataset_info: str, eda_results: str) -> Task:
    return Task(
        description=(
            f"Based on the dataset and EDA results, recommend the best visualizations:\n\n"
            f"Dataset Info:\n{dataset_info}\n\n"
            f"EDA Summary:\n{eda_results}\n\n"
            "Recommend:\n"
            "1. The top 5 most insightful charts to create\n"
            "2. The chart type, columns to use, and what insight each reveals\n"
            "3. Dashboard layout suggestions"
        ),
        expected_output=(
            "A list of recommended visualizations with chart types, column mappings, "
            "and explanations of what insights each visualization would reveal."
        ),
        agent=agent,
    )


def create_ml_task(agent, dataset_info: str, ml_results: str) -> Task:
    return Task(
        description=(
            f"Evaluate the machine learning results and provide recommendations:\n\n"
            f"Dataset Info:\n{dataset_info}\n\n"
            f"ML Results:\n{ml_results}\n\n"
            "Provide:\n"
            "1. Assessment of model performance\n"
            "2. Feature importance analysis\n"
            "3. Recommendations for model improvement\n"
            "4. Potential risks and limitations\n"
            "5. Deployment readiness assessment"
        ),
        expected_output=(
            "A thorough ML evaluation report with performance analysis, "
            "feature importance interpretation, improvement suggestions, "
            "and deployment recommendations."
        ),
        agent=agent,
    )


def create_business_insights_task(agent, full_analysis: str) -> Task:
    return Task(
        description=(
            f"Based on the complete data analysis, generate business insights:\n\n"
            f"{full_analysis}\n\n"
            "Provide:\n"
            "1. Top 5 actionable business insights\n"
            "2. Identified risks and opportunities\n"
            "3. Strategic recommendations\n"
            "4. KPIs to monitor\n"
            "5. Next steps for the business team"
        ),
        expected_output=(
            "A business-focused report with actionable insights, "
            "risk assessment, strategic recommendations, and KPIs."
        ),
        agent=agent,
    )


def create_report_task(agent, full_analysis: str) -> Task:
    return Task(
        description=(
            f"Compile all analysis findings into a professional report:\n\n"
            f"{full_analysis}\n\n"
            "The report should include:\n"
            "1. Executive Summary (2-3 paragraphs)\n"
            "2. Dataset Overview\n"
            "3. Data Quality Assessment\n"
            "4. Key Statistical Findings\n"
            "5. Visualization Insights\n"
            "6. Machine Learning Results (if applicable)\n"
            "7. Business Recommendations\n"
            "8. Appendix with technical details"
        ),
        expected_output=(
            "A complete, professional analysis report with all sections "
            "filled in, ready for stakeholder presentation."
        ),
        agent=agent,
    )


def create_qa_task(agent, report: str) -> Task:
    return Task(
        description=(
            f"Validate the following analysis report for accuracy and quality:\n\n"
            f"{report}\n\n"
            "Check for:\n"
            "1. Statistical accuracy\n"
            "2. Logical consistency\n"
            "3. Potential hallucinations or unfounded claims\n"
            "4. Missing important findings\n"
            "5. Clarity and readability"
        ),
        expected_output=(
            "A QA validation report with identified issues, corrections, "
            "and a confidence score for the overall analysis quality."
        ),
        agent=agent,
    )
