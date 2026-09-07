"""
Automated unit and integration tests for Person 4 AIDA pipeline modules.
"""

import sys
import os
import pandas as pd
import numpy as np

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipeline.visualization import AutoChartEngine
from app.pipeline.dashboard import DashboardAssembler
from fastapi.testclient import TestClient
from main import app


def test_auto_chart_engine():
    print("Testing AutoChartEngine...")
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2026-01-01", periods=n)
    categories = np.random.choice(["Tier A", "Tier B", "Tier C"], size=n)
    revenue = np.random.normal(500, 50, size=n)
    cost = revenue * 0.6 + np.random.normal(0, 10, size=n)
    profit = revenue - cost

    df = pd.DataFrame({
        "date": dates,
        "segment": categories,
        "revenue": revenue,
        "cost": cost,
        "profit": profit
    })

    engine = AutoChartEngine(max_charts=5)
    charts = engine.analyze_and_generate(df, target_col="revenue")

    assert len(charts) > 0, "Charts should not be empty"
    categories_found = {c["category"] for c in charts}
    print(f"Generated {len(charts)} charts with categories: {categories_found}")
    assert "time_series" in categories_found, "Should generate time series chart"
    assert "correlation" in categories_found, "Should generate correlation chart"
    print("AutoChartEngine: PASS")


def test_dashboard_assembler():
    print("Testing DashboardAssembler...")
    discovery = {
        "fingerprint": {
            "shape": [5000, 12],
            "has_datetime": True,
            "recommended_task": "classification"
        },
        "quality_report": {
            "overall_score": 96.5,
            "missing_cells_total": 4,
            "total_rows": 5000,
            "total_cols": 12
        },
        "leakage_report": {
            "has_leakage": False,
            "warnings": []
        }
    }

    analysis = {
        "task_type": "classification",
        "champion_model": "LightGBM Classifier",
        "models": [
            {
                "model_id": "m1",
                "model_name": "LightGBM Classifier",
                "is_champion": True,
                "metrics": {"roc_auc": 0.88, "accuracy": 0.84}
            }
        ]
    }

    contract = DashboardAssembler.assemble(
        dataset_id="test-123",
        dataset_name="test.csv",
        discovery=discovery,
        analysis=analysis,
        insights=[{"id": "ins-1", "title": "Test Insight"}],
        charts=[{"id": "c1", "category": "correlation", "applicable": True}]
    )

    assert contract["dataset_id"] == "test-123"
    assert len(contract["kpis"]) == 4
    assert contract["applicable_sections"]["time_series"] is True
    assert contract["applicable_sections"]["model_championship"] is True
    print("DashboardAssembler: PASS")


def test_pipeline_api_endpoints():
    print("Testing Pipeline REST API endpoints...")
    client = TestClient(app)

    # Test sample contracts
    res_sample = client.get("/api/pipeline/contracts/sample")
    assert res_sample.status_code == 200, f"Sample contracts returned {res_sample.status_code}"
    sample_data = res_sample.json()
    assert "churn_dataset" in sample_data
    assert "sales_forecast" in sample_data
    print("GET /api/pipeline/contracts/sample: PASS")

    # Test dashboard contract
    res_dash = client.get("/api/pipeline/dashboard/demo-churn")
    assert res_dash.status_code == 200
    dash_data = res_dash.json()
    assert "kpis" in dash_data
    assert "charts" in dash_data
    print("GET /api/pipeline/dashboard/demo-churn: PASS")

    # Test championship
    res_champ = client.get("/api/pipeline/championship/demo-churn")
    assert res_champ.status_code == 200
    champ_data = res_champ.json()
    assert "models" in champ_data
    print("GET /api/pipeline/championship/demo-churn: PASS")

    # Test pipeline status
    res_status = client.get("/api/pipeline/status/demo-churn")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert "stages" in status_data
    print("GET /api/pipeline/status/demo-churn: PASS")


if __name__ == "__main__":
    test_auto_chart_engine()
    test_dashboard_assembler()
    test_pipeline_api_endpoints()
    print("\nALL AIDA PERSON 4 PIPELINE TESTS PASSED!")
