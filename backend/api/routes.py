"""
FastAPI route definitions for DataMind AI.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import shutil
import os
import uuid
import json

from sqlalchemy import func
from database.session import get_db
from database.models import User, Dataset, AnalysisHistory, ChatHistory, MLModel
from database.schemas import (
    DatasetResponse, DatasetPreview, AnalyzeRequest, AnalysisResponse,
    ChatRequest, ChatResponse, VisualizeRequest, VisualizationResponse,
    TrainModelRequest, ModelResponse, ReportResponse, DashboardStats,
    RecentActivity, UserResponse, UserCreate, UserLogin, TokenResponse,
    UserPreferencesUpdate
)
from auth import get_current_user, hash_password, verify_password, create_access_token
from config import settings
from tools.analysis_tools import load_dataset, get_dataset_overview, clean_dataset, perform_eda, generate_chart_data, preprocess_for_visualization
from tools.ml_tools import train_classification_model, train_regression_model, train_clustering_model, save_model
from agents.crew import AnalysisCrew, get_llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

router = APIRouter()

# ─── Users ─────────────────────────────────────────────────────

@router.get("/users/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user details."""
    return current_user


@router.put("/users/me/preferences", response_model=UserResponse)
def update_preferences(
    prefs: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user preferences (theme, notifications, data sharing)."""
    existing = current_user.preferences or {"theme": "system", "email_notifs": True, "data_sharing": False}
    update_data = prefs.model_dump(exclude_none=True)
    existing.update(update_data)
    current_user.preferences = existing
    # Force SQLAlchemy to detect the JSON mutation
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "preferences")
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/users/me/password")
def change_password(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change the current user's password."""
    current_pw = payload.get("current_password", "")
    new_pw = payload.get("new_password", "")

    if not verify_password(current_pw, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(new_pw) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    current_user.hashed_password = hash_password(new_pw)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    user = db.query(User).filter((User.email == user_in.email) | (User.username == user_in.username)).first()
    if user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
        
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_in.password)
    db_user = User(
        id=user_id,
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        full_name=user_in.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate token
    access_token = create_access_token(data={"sub": db_user.id})
    return TokenResponse(access_token=access_token, user=db_user)


@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a token."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=access_token, user=user)

# ─── Datasets ──────────────────────────────────────────────────

@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new dataset."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".xlsx", ".xls", ".json"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        df = load_dataset.invoke({"file_path": file_path})
        overview = get_dataset_overview.invoke({"df": df})
        
        dataset = Dataset(
            id=file_id,
            name=file.filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=ext[1:],
            file_size=os.path.getsize(file_path),
            row_count=overview["shape"]["rows"],
            column_count=overview["shape"]["columns"],
            columns_metadata=overview["columns"],
            owner_id=current_user.id,
            status="ready"
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        return dataset
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for the dashboard."""
    total_datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).count()
    analyses_run = db.query(AnalysisHistory).join(Dataset).filter(Dataset.owner_id == current_user.id).count()
    models_trained = db.query(MLModel).join(Dataset).filter(Dataset.owner_id == current_user.id).count()
    
    # Calculate storage
    total_bytes = db.query(func.sum(Dataset.file_size)).filter(Dataset.owner_id == current_user.id).scalar() or 0
    if total_bytes < 1024 * 1024:
        storage_str = f"{total_bytes / 1024:.1f} KB"
    elif total_bytes < 1024 * 1024 * 1024:
        storage_str = f"{total_bytes / (1024 * 1024):.1f} MB"
    else:
        storage_str = f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"
        
    return DashboardStats(
        total_datasets=total_datasets,
        analyses_run=analyses_run,
        models_trained=models_trained,
        storage_used=storage_str
    )

@router.get("/dashboard/recent-activity", response_model=List[RecentActivity])
def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent activity across all user assets."""
    activities = []
    
    # Get recent datasets
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).order_by(Dataset.created_at.desc()).limit(5).all()
    for d in datasets:
        activities.append({
            "id": d.id,
            "activity_type": "dataset",
            "description": f"Uploaded dataset '{d.name}'",
            "status": d.status,
            "created_at": d.created_at
        })
        
    # Get recent analyses
    # Analyses are tied to datasets, so we join on dataset owner
    analyses = db.query(AnalysisHistory).join(Dataset).filter(Dataset.owner_id == current_user.id).order_by(AnalysisHistory.created_at.desc()).limit(5).all()
    for a in analyses:
        activities.append({
            "id": a.id,
            "activity_type": "analysis",
            "description": f"Ran {a.analysis_type} analysis on '{a.dataset.name}'",
            "status": a.status,
            "created_at": a.created_at
        })
        
    # Get recent models
    models = db.query(MLModel).join(Dataset).filter(Dataset.owner_id == current_user.id).order_by(MLModel.created_at.desc()).limit(5).all()
    for m in models:
        activities.append({
            "id": m.id,
            "activity_type": "model",
            "description": f"Trained {m.model_type} model on '{m.dataset.name}'",
            "status": m.status,
            "created_at": m.created_at
        })
        
    # Sort all combined activities by created_at descending and take top 10
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    return activities[:10]

@router.get("/datasets", response_model=List[DatasetResponse])
def get_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all datasets for the current user."""
    return db.query(Dataset).filter(Dataset.owner_id == current_user.id).all()


@router.get("/datasets/{dataset_id}/preview", response_model=DatasetPreview)
def preview_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a preview of the dataset contents."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    try:
        df = load_dataset(dataset.file_path)
        head_data = df.head(10).replace({float('nan'): None}).to_dict(orient="records")
        missing = df.isnull().sum().to_dict()
        
        return DatasetPreview(
            columns=df.columns.tolist(),
            dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
            shape=list(df.shape),
            head=head_data,
            missing_values=missing,
            statistics=df.describe().round(2).to_dict() if not df.empty else {}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/datasets/{dataset_id}")
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a dataset and all associated records."""
    from database.models import AnalysisHistory, ChatHistory, Report, MLModel
    
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Manually delete dependent records
    db.query(AnalysisHistory).filter(AnalysisHistory.dataset_id == dataset.id).delete()
    db.query(ChatHistory).filter(ChatHistory.dataset_id == dataset.id).delete()
    db.query(Report).filter(Report.dataset_id == dataset.id).delete()
    db.query(MLModel).filter(MLModel.dataset_id == dataset.id).delete()
    
    # Try to delete the file
    if os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
        except Exception as e:
            pass # Continue even if file delete fails
            
    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted successfully"}

# ─── Analysis ──────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_dataset(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger automated analysis on a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    analysis = AnalysisHistory(
        dataset_id=dataset.id,
        analysis_type=request.analysis_type,
        status="running",
        parameters=request.parameters
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Route to Celery background task
    from worker import run_analysis_task
    run_analysis_task.delay(analysis.id, dataset.file_path)
    
    return analysis

@router.get("/datasets/{dataset_id}/analyses", response_model=List[AnalysisResponse])
def get_dataset_analyses(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all analyses for a specific dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    analyses = db.query(AnalysisHistory).filter(AnalysisHistory.dataset_id == dataset.id).order_by(AnalysisHistory.created_at.desc()).all()
    return analyses

# ─── Chat ──────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat with the AI Data Analyst."""
    llm = get_llm()
    if not llm:
        raise HTTPException(status_code=500, detail="LLM provider is not configured properly. Check your .env file.")
        
    system_prompt_text = "You are an expert AI Data Analyst. You help the user understand their data, build machine learning models, and create visualizations."
    
    if request.dataset_id:
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id, Dataset.owner_id == current_user.id).first()
        if dataset:
            system_prompt_text += f"\n\nThe user is currently looking at a dataset named '{dataset.name}'. It has {dataset.row_count} rows and {dataset.column_count} columns."
            if dataset.columns_metadata:
                system_prompt_text += f"\nColumns metadata: {json.dumps(dataset.columns_metadata)}"
                
    session_id = request.session_id or str(uuid.uuid4())

    # Fetch history
    history_records = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id,
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.asc()).all()

    chat_history = []
    for record in history_records:
        if record.role == "user":
            chat_history.append(HumanMessage(content=record.content))
        elif record.role == "assistant":
            chat_history.append(AIMessage(content=record.content))

    # Add tools
    tools = [
        load_dataset, get_dataset_overview, clean_dataset, perform_eda, 
        preprocess_for_visualization, generate_chart_data,
        train_classification_model, train_regression_model, 
        train_clustering_model, save_model
    ]

    from langgraph.prebuilt import create_react_agent
    
    agent_executor = create_react_agent(llm, tools=tools, state_modifier=system_prompt_text)

    try:
        # Save user message
        db_user_msg = ChatHistory(
            session_id=session_id,
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            role="user",
            content=request.message
        )
        db.add(db_user_msg)
        db.commit()

        # Run agent
        result = agent_executor.invoke({
            "messages": chat_history + [HumanMessage(content=request.message)]
        })
        final_response = result["messages"][-1].content

        # Save AI message
        db_ai_msg = ChatHistory(
            session_id=session_id,
            user_id=current_user.id,
            dataset_id=request.dataset_id,
            role="assistant",
            content=final_response
        )
        db.add(db_ai_msg)
        db.commit()

        return ChatResponse(
            response=final_response,
            session_id=session_id
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error communicating with LLM: {str(e)}")

# ─── Visualizations ────────────────────────────────────────────

@router.post("/visualize", response_model=VisualizationResponse)
def generate_visualization(
    request: VisualizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a specific visualization."""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    df = load_dataset.invoke({"file_path": dataset.file_path})
    chart_data = generate_chart_data.invoke({
        "df": df, 
        "chart_type": request.chart_type, 
        "x_column": request.x_column, 
        "y_column": request.y_column, 
        "color_column": request.color_column
    })
    
    # Build insights from preprocessing steps performed
    preprocess_steps = chart_data.pop("preprocessing_steps", [])
    n_rows = len(df)
    if preprocess_steps:
        insights = f"Dataset: {n_rows} rows used (full dataset). Preprocessing applied: " + " | ".join(preprocess_steps)
    else:
        insights = f"Dataset: {n_rows} rows used. No preprocessing was needed (data was already clean)."
    
    return VisualizationResponse(
        chart_type=request.chart_type,
        chart_data=chart_data,
        insights=insights
    )

# ─── ML Models ─────────────────────────────────────────────────

@router.post("/train-model", response_model=ModelResponse)
def train_ml_model(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Train a machine learning model."""
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    model_record = MLModel(
        name=f"{request.model_type.capitalize()} on {dataset.name}",
        dataset_id=dataset.id,
        model_type=request.model_type,
        algorithm=request.algorithm or "auto",
        target_column=request.target_column,
        feature_columns=request.feature_columns,
        hyperparameters=request.hyperparameters,
        status="training"
    )
    db.add(model_record)
    db.commit()
    db.refresh(model_record)
    
    def run_training_task(model_id: str, file_path: str, req: TrainModelRequest):
        from database.session import SessionLocal
        bg_db = SessionLocal()
        try:
            db_model = bg_db.query(MLModel).filter(MLModel.id == model_id).first()
            df = load_dataset.invoke({"file_path": file_path})
            
            result = None
            if req.model_type == "classification":
                result = train_classification_model.invoke({"df": df, "target_column": req.target_column, "algorithm": req.algorithm or "random_forest", "feature_columns": req.feature_columns, "hyperparameters": req.hyperparameters})
            elif req.model_type == "regression":
                result = train_regression_model.invoke({"df": df, "target_column": req.target_column, "algorithm": req.algorithm or "random_forest", "feature_columns": req.feature_columns, "hyperparameters": req.hyperparameters})
            elif req.model_type == "clustering":
                result = train_clustering_model.invoke({"df": df, "algorithm": req.algorithm or "kmeans", "feature_columns": req.feature_columns, "hyperparameters": req.hyperparameters})
                
            if result and "error" not in result:
                db_model.metrics = result["metrics"]
                db_model.algorithm = result["algorithm"]
                db_model.status = "ready"
                
                # Save model file
                model_dir = os.path.join(settings.UPLOAD_DIR, "models")
                os.makedirs(model_dir, exist_ok=True)
                model_path = os.path.join(model_dir, f"{model_id}.pkl")
                save_model.invoke({"model_data": result, "path": model_path})
                db_model.model_path = model_path
            else:
                db_model.status = "failed"
                
            bg_db.commit()
        except Exception as e:
            db_model.status = "failed"
            bg_db.commit()
        finally:
            bg_db.close()
            
    background_tasks.add_task(run_training_task, model_record.id, dataset.file_path, request)
    
    return model_record

@router.get("/models", response_model=List[ModelResponse])
def get_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all trained models for the current user."""
    models = db.query(MLModel).join(Dataset).filter(Dataset.owner_id == current_user.id).order_by(MLModel.created_at.desc()).all()
    return models
