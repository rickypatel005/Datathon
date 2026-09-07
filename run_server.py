"""Server entrypoint to run AIDA Trust Layer FastAPI application."""

import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  🧠 Starting AIDA Trust Layer API Server")
    print("  Endpoint: http://localhost:8000")
    print("  Docs:     http://localhost:8000/docs")
    print("  Health:   http://localhost:8000/health")
    print("=" * 60)
    uvicorn.run(
        "backend.aida.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
