"""
AIDA Discovery Contract (Person 1 -> Person 2/3/4).
Defines the canonical machine-readable schema for dataset discovery,
quality auditing, dataset fingerprinting, leakage analysis, and task routing.
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class InferredDtype(str, Enum):
    NUMERIC_CONTINUOUS = "numeric_continuous"
    NUMERIC_DISCRETE = "numeric_discrete"
    CATEGORICAL_NOMINAL = "categorical_nominal"
    CATEGORICAL_ORDINAL = "categorical_ordinal"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    IDENTIFIER = "identifier"
    TEXT = "text"
    FREE_TEXT = "free_text"
    UNKNOWN = "unknown"


class TaskType(str, Enum):
    BINARY_CLASSIFICATION = "binary_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES_FORECASTING = "time_series_forecasting"
    UNSUPERVISED_EDA = "unsupervised_eda"


class ValidationStrategy(str, Enum):
    STRATIFIED_K_FOLD = "StratifiedKFold"
    K_FOLD = "KFold"
    WALK_FORWARD = "WalkForward"
    GROUP_K_FOLD = "GroupKFold"
    TIME_SERIES_SPLIT = "TimeSeriesSplit"
    STANDARD_SPLIT = "StandardSplit"


class LeakageRiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class LeakageType(str, Enum):
    TARGET_DERIVED = "target_derived"
    FUTURE_POST_EVENT = "future_post_event"
    POST_EVENT = "post_event"
    FUTURE = "future"
    SUSPICIOUS_CORRELATION = "suspicious_correlation"
    SUSPICIOUS_PREDICTIVE = "suspicious_predictive"
    ID_LEAKAGE = "id_leakage"
    ID_CONTAMINATION = "id_contamination"
    CONSTANT_LEAKAGE = "constant_leakage"
    DUPLICATE_FEATURE = "duplicate_feature"


class LeakageRecommendation(str, Enum):
    USE = "use"
    USE_WITH_WARNING = "use_with_warning"
    REVIEW = "review"
    EXCLUDE_FROM_MODEL = "exclude_from_model"


# ─── Sub-models ──────────────────────────────────────────────────

class FileInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    file_path: str
    file_type: str  # csv, xlsx, xls, json
    file_size_bytes: int
    row_count: int
    column_count: int
    encoding: Optional[str] = "utf-8"
    delimiter: Optional[str] = ","
    sheet_name: Optional[str] = None


class ColumnStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    median: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    top_frequencies: Optional[Dict[str, int]] = None
    mode: Optional[Any] = None


class ColumnMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    raw_dtype: str
    inferred_type: InferredDtype
    subtype: Optional[str] = None
    confidence: float = 1.0
    reasons: List[str] = Field(default_factory=list)
    null_count: int
    null_percentage: float
    unique_count: int
    cardinality_ratio: float
    is_identifier: bool = False
    is_potential_target: bool = False
    is_constant: bool = False
    sample_values: List[Any] = Field(default_factory=list)
    stats: Optional[ColumnStats] = None


class TemporalProperties(BaseModel):
    model_config = ConfigDict(extra="ignore")

    temporal_column: Optional[str] = None
    candidate_date_columns: List[str] = Field(default_factory=list)
    is_sorted: bool = False
    is_monotonic: bool = False
    inferred_frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    distinct_dates_count: Optional[int] = None
    has_gaps: bool = False
    temporal_completeness_ratio: Optional[float] = None
    is_regularly_spaced: bool = False


class ClassBalance(BaseModel):
    model_config = ConfigDict(extra="ignore")

    target_column: str
    proportions: Dict[str, float]
    class_counts: Dict[str, int]
    minority_class: Optional[str] = None
    minority_class_percentage: float
    is_imbalanced: bool = False
    imbalance_ratio: float = 1.0


class DatasetFingerprint(BaseModel):
    model_config = ConfigDict(extra="ignore")

    shape: List[int]  # [rows, cols]
    memory_mb: float
    dataset_summary: Optional[str] = None
    numeric_columns: List[str] = Field(default_factory=list)
    categorical_columns: List[str] = Field(default_factory=list)
    datetime_columns: List[str] = Field(default_factory=list)
    identifier_columns: List[str] = Field(default_factory=list)
    text_columns: List[str] = Field(default_factory=list)
    constant_columns: List[str] = Field(default_factory=list)
    high_cardinality_categoricals: List[str] = Field(default_factory=list)
    primary_entity_key: Optional[str] = None
    temporal: Optional[TemporalProperties] = None
    class_balance: Optional[ClassBalance] = None
    missingness_summary: Optional[Dict[str, Any]] = None
    cardinality_summary: Optional[Dict[str, int]] = None
    quality_warnings: List[str] = Field(default_factory=list)
    task_type_candidates: List[TaskType] = Field(default_factory=list)


class TypeMismatch(BaseModel):
    model_config = ConfigDict(extra="ignore")

    column: str
    declared_type: str
    detected_irregularities: str
    count: int


class QualityReport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    overall_quality_score: float = Field(ge=0.0, le=100.0)
    score_breakdown: Optional[Dict[str, float]] = None
    duplicate_row_count: int = 0
    duplicate_row_percentage: float = 0.0
    unique_row_count: Optional[int] = None
    total_missing_cells: int = 0
    missing_cell_percentage: float = 0.0
    columns_with_missing: List[str] = Field(default_factory=list)
    column_missingness: Optional[Dict[str, Dict[str, Any]]] = None
    columns_with_outliers: List[str] = Field(default_factory=list)
    total_outliers: int = 0
    outlier_details: Optional[Dict[str, Dict[str, Any]]] = None
    constant_columns: Optional[List[Dict[str, Any]]] = None
    near_constant_columns: Optional[List[Dict[str, Any]]] = None
    high_cardinality_issues: Optional[List[Dict[str, Any]]] = None
    categorical_inconsistencies: Optional[List[Dict[str, Any]]] = None
    type_mismatches: List[TypeMismatch] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    passed_checks: List[str] = Field(default_factory=list)


class IdentifierIsolation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    column: str
    identifier_type: str
    uniqueness_ratio: float
    target_association: Optional[float] = None
    recommended_use: str = "exclude_from_model"
    reason: str


class LeakageCandidate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    column: str
    leakage_type: LeakageType
    risk_level: LeakageRiskLevel
    reason: str
    reasons: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    evidence: Dict[str, Any] = Field(default_factory=dict)
    recommendation: str = "exclude_from_model"
    target_column: Optional[str] = None
    correlation_with_target: Optional[float] = None


class LeakageReport(BaseModel):
    model_config = ConfigDict(extra="ignore")

    has_leakage_risk: bool = False
    overall_risk: LeakageRiskLevel = LeakageRiskLevel.NONE
    leakage_candidates: List[LeakageCandidate] = Field(default_factory=list)
    findings: List[LeakageCandidate] = Field(default_factory=list)
    identifiers: List[IdentifierIsolation] = Field(default_factory=list)
    recommended_drops: List[str] = Field(default_factory=list)
    excluded_features: List[str] = Field(default_factory=list)
    review_features: List[str] = Field(default_factory=list)
    sanitized_feature_columns: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class TaskRouteDecision(BaseModel):
    model_config = ConfigDict(extra="ignore")

    task: str
    status: str  # applicable, skipped, unsupported, insufficient_evidence
    reason: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
    target_column: Optional[str] = None
    recommended_validation: Optional[str] = None
    recommended_metrics: List[str] = Field(default_factory=list)


class RouterDecision(BaseModel):
    model_config = ConfigDict(extra="ignore")

    recommended_primary_task: TaskType
    secondary_tasks: List[TaskType] = Field(default_factory=list)
    applicable_engines: List[str] = Field(default_factory=list)
    skipped_engines: Dict[str, str] = Field(default_factory=dict)
    validation_strategy: ValidationStrategy
    recommended_metrics: List[str] = Field(default_factory=list)
    rationale: str
    task_decisions: Optional[Dict[str, TaskRouteDecision]] = None
    usable_feature_columns: List[str] = Field(default_factory=list)
    excluded_identifier_columns: List[str] = Field(default_factory=list)
    excluded_leakage_columns: List[str] = Field(default_factory=list)
    review_feature_columns: List[str] = Field(default_factory=list)
    unsupported_feature_columns: List[str] = Field(default_factory=list)
    validation_rationale: Optional[str] = None
    group_column: Optional[str] = None


class TargetCandidate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    column_name: str
    task_type: TaskType
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    class_count: Optional[int] = None


class ActionRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action_type: str = "custom_action"  # drop_column, drop_duplicates, impute_missing, normalize_whitespace
    action: Optional[str] = None
    column: Optional[str] = None
    affected_rows: int = 0
    description: str = ""
    reason: Optional[str] = None
    method: Optional[str] = None
    before_summary: Optional[Dict[str, Any]] = None
    after_summary: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CleaningAudit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    original_shape: List[int]
    cleaned_shape: List[int]
    applied_actions: List[ActionRecord] = Field(default_factory=list)
    dropped_columns: List[str] = Field(default_factory=list)
    imputed_columns: List[str] = Field(default_factory=list)


# ─── Root Discovery Contract ─────────────────────────────────────

class DiscoveryContract(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str = "1.0.0"
    contract_type: str = "discovery"
    dataset_id: str
    dataset_name: str
    file_info: FileInfo
    columns: List[ColumnMetadata]
    fingerprint: DatasetFingerprint
    quality_report: QualityReport
    leakage_report: LeakageReport
    router: RouterDecision
    target_candidates: List[TargetCandidate] = Field(default_factory=list)
    cleaning_audit: CleaningAudit
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
