import json
from celery import Celery
from config import settings
from database.session import SessionLocal
from database.models import AnalysisHistory
from tools.analysis_tools import load_dataset, clean_dataset, perform_eda
from agents.crew import AnalysisCrew

celery_app = Celery(
    "datamind_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="run_analysis_task")
def run_analysis_task(analysis_id: str, file_path: str):
    bg_db = SessionLocal()
    try:
        db_analysis = bg_db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()
        if not db_analysis:
            return
            
        df = load_dataset.invoke({"file_path": file_path})
        
        # Step 1: Clean
        clean_res = clean_dataset.invoke({"file_path": file_path})
        cleaned_df = clean_res["dataframe"]
        
        # Save cleaned dataset to a temporary file for EDA
        cleaned_path = file_path + "_cleaned.csv"
        cleaned_df.to_csv(cleaned_path, index=False)
        
        # Step 2: EDA
        eda_res = perform_eda.invoke({"file_path": cleaned_path})
        
        # Invoke CrewAI for deep analysis
        dataset_info = f"Dataset size: {cleaned_df.shape[0]} rows, {cleaned_df.shape[1]} columns. Columns: {', '.join(cleaned_df.columns)}"
        crew = AnalysisCrew(dataset_info=dataset_info, analysis_type=db_analysis.analysis_type)
        
        crew_report = crew.run_full_analysis(
            cleaning_report=json.dumps(clean_res["report"]),
            eda_results=json.dumps(eda_res)
        )
        
        db_analysis.result = {
            "cleaning": clean_res["report"],
            "eda": eda_res,
            "crew_report": str(crew_report)
        }
        db_analysis.status = "completed"
        bg_db.commit()
    except Exception as e:
        if 'db_analysis' in locals() and db_analysis:
            db_analysis.status = "failed"
            db_analysis.summary = str(e)
            bg_db.commit()
    finally:
        bg_db.close()
