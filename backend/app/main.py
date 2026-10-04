from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from app.api.v1.endpoints import models, monitoring, incidents

app = FastAPI(
    title="ModelSentinel API",
    version="0.1.0",
)

# CORS setup
origins = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:5173"]')
if isinstance(origins, str):
    try:
        origins = json.loads(origins)
    except Exception:
        origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(monitoring.router, prefix="/api/v1/models/{model_id}/monitoring", tags=["monitoring"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"])

from sqlalchemy import text
from app.db.session import SessionLocal

@app.get("/health")
def health_check():
    db_status = "unknown"
    db_engine = "unknown"
    try:
        db = SessionLocal()
        # Test connection
        db.execute(text("SELECT 1"))
        db_engine = db.bind.dialect.name
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    finally:
        try:
            db.close()
        except:
            pass

    return {
        "status": "ok",
        "service": "modelsentinel-api",
        "version": "0.1.0",
        "database": {
            "status": db_status,
            "engine": db_engine
        }
    }
