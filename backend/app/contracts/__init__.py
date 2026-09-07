"""
Shared machine-readable contracts between AIDA pipeline stages.
All contracts are versioned and strictly typed.
"""
from app.contracts.discovery import (
    DiscoveryContract,
    DatasetFingerprint,
    QualityReport,
    LeakageReport,
    RouterDecision,
    TargetCandidate,
    CleaningAudit,
    ColumnMetadata,
    ColumnStats,
    TypeMismatch,
    LeakageCandidate,
    ActionRecord,
    TaskType,
    ValidationStrategy,
)

__all__ = [
    "DiscoveryContract",
    "DatasetFingerprint",
    "QualityReport",
    "LeakageReport",
    "RouterDecision",
    "TargetCandidate",
    "CleaningAudit",
    "ColumnMetadata",
    "ColumnStats",
    "TypeMismatch",
    "LeakageCandidate",
    "ActionRecord",
    "TaskType",
    "ValidationStrategy",
]
