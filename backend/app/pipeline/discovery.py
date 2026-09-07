"""
Person 1: Full Discovery Pipeline Orchestrator.
Loads unseen CSV/XLSX datasets, performs type inference, fingerprints data,
assesses quality, hunts leakage, determines routing, and outputs a canonical DiscoveryContract.
"""
import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import pandas as pd

from app.contracts.discovery import (
    DiscoveryContract,
    FileInfo,
)
from app.pipeline.loaders import load_dataset
from app.pipeline.fingerprint import generate_fingerprint
from app.pipeline.quality import evaluate_quality
from app.pipeline.leakage import detect_leakage
from app.pipeline.router import route_dataset


def run_discovery(
    file_path: str,
    dataset_id: Optional[str] = None,
    dataset_name: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
) -> DiscoveryContract:
    """
    Execute full Person 1 Discovery pipeline on any unseen tabular file.
    Returns:
        DiscoveryContract (canonical, versioned, machine-readable)
    """
    # 1. Load dataset with robust fallback
    df, file_info_dict = load_dataset(file_path)

    d_id = dataset_id or f"ds-{uuid.uuid4().hex[:12]}"
    d_name = dataset_name or os.path.basename(file_path)

    file_info = FileInfo(
        file_path=file_info_dict["file_path"],
        file_type=file_info_dict["file_type"],
        file_size_bytes=file_info_dict["file_size_bytes"],
        row_count=file_info_dict["row_count"],
        column_count=file_info_dict["column_count"],
        encoding=file_info_dict["encoding"],
        delimiter=file_info_dict["delimiter"],
        sheet_name=file_info_dict.get("sheet_name"),
    )

    # 2. Generate fingerprint, column metadata, and target candidates
    fingerprint, columns_meta, target_candidates = generate_fingerprint(df)

    # 3. Evaluate data quality and audit trail
    quality_report, cleaning_audit, cleaned_df = evaluate_quality(df, columns_meta)

    # 4. Detect leakage risks
    leakage_report = detect_leakage(df, columns_meta, target_candidates, temporal=fingerprint.temporal)

    # 5. Route dataset to analytical tasks
    router_decision = route_dataset(
        fingerprint=fingerprint,
        target_candidates=target_candidates,
        quality_report=quality_report,
        leakage_report=leakage_report,
        columns_meta=columns_meta,
    )

    # 6. Assemble DiscoveryContract
    contract = DiscoveryContract(
        version="1.0.0",
        contract_type="discovery",
        dataset_id=d_id,
        dataset_name=d_name,
        file_info=file_info,
        columns=columns_meta,
        fingerprint=fingerprint,
        quality_report=quality_report,
        leakage_report=leakage_report,
        router=router_decision,
        target_candidates=target_candidates,
        cleaning_audit=cleaning_audit,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=custom_metadata or {},
    )

    return contract
