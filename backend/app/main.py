from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from app.api.v1.endpoints import models, monitoring, incidents, investigations, repositories, patches, validation, memory, regression, pull_requests, deployments, analytics, change_risk, policies, telemetry, reliability, model_intelligence, workflows, integrations

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

from fastapi import Depends
from app.api import deps

app.include_router(models.router, prefix="/api/v1/models", tags=["models"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(monitoring.router, prefix="/api/v1/models/{model_id}/monitoring", tags=["monitoring"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["incidents"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(investigations.router, prefix="/api/v1", tags=["investigations"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(repositories.router, prefix="/api/v1/repositories", tags=["repositories"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(patches.router, prefix="/api/v1", tags=["patches"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(validation.router, prefix="/api/v1", tags=["validation"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(memory.router, prefix="/api/v1", tags=["memory"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(regression.router, prefix="/api/v1", tags=["regression"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(pull_requests.router, prefix="/api/v1/pull-requests", tags=["pull_requests"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["deployments"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(change_risk.router, prefix="/api/v1/change-risk", tags=["change_risk"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["telemetry"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(reliability.router, prefix="/api/v1/models/{model_id}/reliability", tags=["reliability"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(model_intelligence.router, prefix="/api/v1/models", tags=["intelligence"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
from app.api.v1.endpoints import ci, auth, audit
app.include_router(ci.router, prefix="/api/v1/ci", tags=["ci"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"], dependencies=[Depends(deps.get_current_active_user)])
from sqlalchemy import text
from app.db.session import SessionLocal
from app.ai.service import get_llm_provider

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

    provider_status = "unavailable"
    try:
        provider = get_llm_provider()
        if provider.health_check():
            provider_status = "configured"
        else:
            provider_status = "misconfigured"
    except Exception:
        provider_status = "unavailable"

    return {
        "status": "ok",
        "service": "modelsentinel-api",
        "version": "0.1.0",
        "database": {
            "status": db_status,
            "engine": db_engine
        },
        "ai_provider": {
            "status": provider_status
        }
    }
