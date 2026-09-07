"""
Tests for Person 1 Setup, Shared Contracts, Loaders, and Discovery Pipeline.
"""
import os
import json
import pytest
import pandas as pd

from app.contracts.discovery import (
    DiscoveryContract,
    DatasetFingerprint,
    QualityReport,
    LeakageReport,
    RouterDecision,
    TargetCandidate,
    TaskType,
    ValidationStrategy,
)
from app.pipeline.loaders import load_dataset, detect_csv_dialect
from app.pipeline.discovery import run_discovery


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "data")
MOCK_FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "app", "contracts", "fixtures", "discovery_mock.json"
)


def test_mock_discovery_json_fixture_validates():
    """Verify that the mock Discovery Contract JSON exists, is valid JSON, and matches the Pydantic schema."""
    assert os.path.exists(MOCK_FIXTURE_PATH), f"Mock fixture missing at {MOCK_FIXTURE_PATH}"
    
    with open(MOCK_FIXTURE_PATH, "r", encoding="utf-8") as f:
        mock_data = json.load(f)
        
    contract = DiscoveryContract.model_validate(mock_data)
    assert contract.version == "1.0.0"
    assert contract.contract_type == "discovery"
    assert contract.dataset_id == "ds-mock-churn-001"
    assert contract.fingerprint.primary_entity_key == "CustomerId"
    assert contract.quality_report.overall_quality_score > 0
    assert contract.leakage_report.has_leakage_risk is True
    assert "CustomerId" in contract.leakage_report.recommended_drops
    assert contract.router.recommended_primary_task == TaskType.BINARY_CLASSIFICATION
    assert contract.router.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD
    assert len(contract.target_candidates) >= 1
    assert contract.target_candidates[0].column_name == "Exited"


def test_csv_loading_standard():
    """Test loading standard CSV dataset."""
    csv_path = os.path.join(FIXTURES_DIR, "churn_classification.csv")
    df, info = load_dataset(csv_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    assert info["file_type"] == "csv"
    assert info["delimiter"] == ","
    assert info["row_count"] == 100
    assert info["column_count"] == 6


def test_xlsx_loading():
    """Test loading XLSX Excel workbook using openpyxl."""
    xlsx_path = os.path.join(FIXTURES_DIR, "sample_workbook.xlsx")
    df, info = load_dataset(xlsx_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 20
    assert info["file_type"] == "xlsx"
    assert info["row_count"] == 20
    assert "product_id" in df.columns


def test_csv_loading_adversarial_delimiter_and_encoding():
    """Test loading adversarial CSV with semicolon delimiter and Latin-1 characters."""
    adv_path = os.path.join(FIXTURES_DIR, "adversarial_dataset.csv")
    df, info = load_dataset(adv_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6
    assert info["delimiter"] == ";"
    assert "René" in df["name"].values or "Zöe" in df["name"].values


def test_discovery_pipeline_on_classification_data():
    """Test full run_discovery pipeline on classification data."""
    csv_path = os.path.join(FIXTURES_DIR, "churn_classification.csv")
    contract = run_discovery(csv_path)
    
    assert isinstance(contract, DiscoveryContract)
    assert contract.version == "1.0.0"
    assert contract.file_info.row_count == 100
    assert "customer_id" in contract.fingerprint.identifier_columns
    assert contract.fingerprint.primary_entity_key == "customer_id"
    assert contract.router.recommended_primary_task == TaskType.BINARY_CLASSIFICATION
    assert contract.router.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD
    assert "customer_id" in contract.leakage_report.recommended_drops


def test_discovery_pipeline_on_regression_data():
    """Test full run_discovery pipeline on regression data."""
    csv_path = os.path.join(FIXTURES_DIR, "housing_regression.csv")
    contract = run_discovery(csv_path)
    
    assert isinstance(contract, DiscoveryContract)
    assert contract.version == "1.0.0"
    assert contract.router.recommended_primary_task == TaskType.REGRESSION
    assert contract.router.validation_strategy == ValidationStrategy.K_FOLD
    assert "price" in [tc.column_name for tc in contract.target_candidates]


def test_discovery_pipeline_on_excel():
    """Test full run_discovery pipeline on Excel workbook."""
    xlsx_path = os.path.join(FIXTURES_DIR, "sample_workbook.xlsx")
    contract = run_discovery(xlsx_path)
    
    assert isinstance(contract, DiscoveryContract)
    assert contract.file_info.file_type == "xlsx"
    assert contract.quality_report.overall_quality_score >= 80.0
    assert contract.router.validation_strategy is not None


def test_discovery_contract_serialization_roundtrip():
    """Verify that DiscoveryContract serializes to JSON and deserializes back losslessly."""
    csv_path = os.path.join(FIXTURES_DIR, "churn_classification.csv")
    contract = run_discovery(csv_path)
    
    json_str = contract.model_dump_json()
    contract_data = json.loads(json_str)
    
    restored = DiscoveryContract.model_validate(contract_data)
    assert restored.version == contract.version
    assert restored.dataset_id == contract.dataset_id
    assert restored.fingerprint.shape == contract.fingerprint.shape
    assert restored.router.recommended_primary_task == contract.router.recommended_primary_task
