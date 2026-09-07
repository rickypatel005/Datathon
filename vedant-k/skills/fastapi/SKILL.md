---
name: fastapi
description: FastAPI backend architecture, Pydantic v2 schemas, and dependency injection.
---

# FastAPI Best Practices

## Principles
1. **Pydantic v2 Strict Typing**: Strict models for all request bodies, responses, and pipeline contracts.
2. **Modular APIRouter**: Keep routers focused by domain (`/pipeline`, `/contracts`, `/health`).
3. **Async Non-blocking Handlers**: Offload heavy CPU-bound ML computations to threadpools (`run_in_threadpool`) or background tasks.
4. **Structured Error Handling**: Explicit HTTPException mapping with machine-readable error codes.
