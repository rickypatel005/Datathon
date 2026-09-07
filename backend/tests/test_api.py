"""Tests for AIDA FastAPI application and endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.aida.api import app
from backend.aida.mocks.mock_contracts import (
    get_mock_discovery_contract,
    get_mock_analysis_contract,
)

client = TestClient(app)


def test_health_check_endpoint():
    """Verify /health returns 200 and online status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "Trust Layer Online"}


def test_generate_insights_endpoint_success():
    """Verify POST /api/v1/insights runs full pipeline and returns unified payload for UI."""
    discovery = get_mock_discovery_contract()
    analysis = get_mock_analysis_contract()

    payload = {
        "discovery_contract": discovery.model_dump(),
        "analysis_contract": analysis.model_dump(),
    }

    response = client.post("/api/v1/insights", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "dataset_id" in body
    assert body["dataset_id"] == discovery.dataset_id
    assert body["status"] == "SUCCESS"

    # Executive Summary for Person 4
    assert "summary" in body
    summary = body["summary"]
    assert "top_3_insights" in summary
    assert len(summary["top_3_insights"]) > 0
    assert "executive_summary_text" in summary
    assert "verification_pass_rate" in summary

    # Verified Insights List
    assert "verified_insights" in body
    verified = body["verified_insights"]
    assert len(verified) > 0
    for vi in verified:
        assert vi["status"] == "VERIFIED"
        assert vi["confidence_score"] > 0.0
        assert len(vi["evidence"]) > 0

    # Rejected Insights Audit List
    assert "rejected_insights" in body


def test_generate_insights_endpoint_graceful_with_empty_contracts():
    """Endpoint must gracefully handle empty dict contracts without throwing a 500."""
    payload = {
        "discovery_contract": {},
        "analysis_contract": {},
    }

    response = client.post("/api/v1/insights", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "verified_insights" in body
