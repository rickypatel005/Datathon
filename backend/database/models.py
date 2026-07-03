"""
SQLAlchemy ORM models for DataMind AI.
Defines: User, Dataset, AnalysisHistory, ChatHistory, Report, MLModel
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database.session import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default="analyst")  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    preferences = Column(JSON, default=lambda: {"theme": "system", "email_notifs": True, "data_sharing": False})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    datasets = relationship("Dataset", back_populates="owner")
    reports = relationship("Report", back_populates="owner")
    chat_histories = relationship("ChatHistory", back_populates="user")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)  # csv, xlsx, json
    file_size = Column(Integer)  # bytes
    row_count = Column(Integer)
    column_count = Column(Integer)
    columns_metadata = Column(JSON)  # {"col_name": {"dtype": "...", "null_count": 0, ...}}
    description = Column(Text)
    status = Column(String(50), default="uploaded")  # uploaded, analyzing, ready, error
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="datasets")
    analyses = relationship("AnalysisHistory", back_populates="dataset")
    chat_histories = relationship("ChatHistory", back_populates="dataset")
    ml_models = relationship("MLModel", back_populates="dataset")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    analysis_type = Column(String(100), nullable=False)  # eda, cleaning, visualization, ml, full
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    parameters = Column(JSON)  # Input parameters for the analysis
    result = Column(JSON)  # Structured result output
    summary = Column(Text)  # Natural language summary
    agent_logs = Column(JSON)  # Logs from CrewAI agents
    duration_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    dataset = relationship("Dataset", back_populates="analyses")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON)  # Extra info: charts, tables, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_histories")
    dataset = relationship("Dataset", back_populates="chat_histories")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(500), nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), default="full")  # full, eda, ml, summary
    content = Column(JSON)  # Structured report sections
    html_content = Column(Text)  # Rendered HTML version
    file_path = Column(String(500))  # Path to exported PDF/DOCX
    status = Column(String(50), default="generating")  # generating, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="reports")
    dataset = relationship("Dataset")


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    model_type = Column(String(100), nullable=False)  # classification, regression, clustering
    algorithm = Column(String(100), nullable=False)  # random_forest, xgboost, kmeans, etc.
    target_column = Column(String(255))
    feature_columns = Column(JSON)  # List of feature column names
    hyperparameters = Column(JSON)
    metrics = Column(JSON)  # {"accuracy": 0.95, "f1": 0.92, ...}
    model_path = Column(String(500))  # Path to saved model pickle
    status = Column(String(50), default="training")  # training, ready, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("Dataset", back_populates="ml_models")
