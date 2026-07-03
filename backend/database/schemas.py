"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── Auth ──────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    theme: Optional[str] = None
    email_notifs: Optional[bool] = None
    data_sharing: Optional[bool] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Dataset ──────────────────────────────────────────────────
class DatasetResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    file_type: str
    file_size: Optional[int] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    columns_metadata: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetPreview(BaseModel):
    columns: List[str]
    dtypes: Dict[str, str]
    shape: List[int]
    head: List[Dict[str, Any]]
    missing_values: Dict[str, int]
    statistics: Dict[str, Any]


# ─── Analysis ─────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    dataset_id: str
    analysis_type: str = "full"  # full, eda, cleaning, visualization, ml
    parameters: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    id: str
    dataset_id: str
    analysis_type: str
    status: str
    result: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat ──────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    dataset_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None


# ─── Visualization ────────────────────────────────────────────
class VisualizeRequest(BaseModel):
    dataset_id: str
    chart_type: str  # histogram, scatter, bar, pie, heatmap, boxplot, line
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class VisualizationResponse(BaseModel):
    chart_type: str
    chart_data: Dict[str, Any]  # Plotly JSON figure
    insights: Optional[str] = None


# ─── ML Model ─────────────────────────────────────────────────
class TrainModelRequest(BaseModel):
    dataset_id: str
    model_type: str  # classification, regression, clustering
    algorithm: Optional[str] = None  # auto-select if not provided
    target_column: Optional[str] = None  # Not needed for clustering
    feature_columns: Optional[List[str]] = None  # Use all if not provided
    hyperparameters: Optional[Dict[str, Any]] = None


class ModelResponse(BaseModel):
    id: str
    name: str
    model_type: str
    algorithm: str
    metrics: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Report ────────────────────────────────────────────────────
class ReportResponse(BaseModel):
    id: str
    title: str
    dataset_id: str
    report_type: str
    content: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ─── Dashboard ────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_datasets: int
    analyses_run: int
    models_trained: int
    storage_used: str

class RecentActivity(BaseModel):
    id: str
    activity_type: str  # e.g., 'dataset_uploaded', 'analysis_completed', 'model_trained'
    description: str
    status: str
    created_at: datetime

