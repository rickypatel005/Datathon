from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.session import engine, Base

# Import models to ensure they are registered with SQLAlchemy
from database import models

# Create all tables
Base.metadata.create_all(bind=engine)

from api.routes import router as api_router

app = FastAPI(
    title="DataMind AI API",
    description="Backend API for the Autonomous Data Analyst Agent",
    version="1.0.0"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to DataMind AI API"}
# trigger reload
