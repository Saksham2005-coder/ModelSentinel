from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from app.api.v1.endpoints import models, monitoring, incidents, investigations, repositories, patches, validation, memory, regression, pull_requests, deployments, analytics, change_risk, policies, telemetry, reliability, model_intelligence, workflows, integrations

app = FastAPI(
    title="ModelSentinel API",
    version="0.1.0",
)

# CORS setup - allow all origins for deployment/preview flexibility
origins = os.getenv("BACKEND_CORS_ORIGINS", "*")
if isinstance(origins, str) and origins != "*":
    try:
        origins = json.loads(origins)
    except Exception:
        origins = [origins]
elif origins == "*":
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import time
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        if len(request_id) > 64:
            request_id = str(uuid.uuid4())
        
        request.state.request_id = request_id
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as exc:
            raise exc
        finally:
            process_time = (time.time() - start_time) * 1000.0
            # Could log here: logger.info(f"[{request_id}] {request.method} {request.url.path} - {process_time:.2f}ms")
            
        response.headers["X-Request-ID"] = request_id
        return response

app.add_middleware(RequestIDMiddleware)

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
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"], dependencies=[Depends(deps.get_current_active_user), Depends(deps.RequirePermissions(["analytics.read"]))])
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
from app.api.v1.endpoints import slo, alerts
app.include_router(slo.router, prefix="/api/v1/slo", tags=["slo"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"], dependencies=[Depends(deps.get_current_active_user)])
from sqlalchemy import text
from app.db.session import SessionLocal
from app.ai.service import get_llm_provider
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import traceback
import uuid

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.error(f"Unhandled exception (Error ID: {error_id}): {exc}")
    logger.error(traceback.format_exc())
    # Return a safe error message without exposing stack traces or database details
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred.", "error_id": error_id},
    )

@app.on_event("startup")
def bootstrap_admin():
    from app.db.session import SessionLocal
    from app.models.user import User, Role
    from app.core import security
    db = SessionLocal()
    try:
        admin_email = "admin@modelsentinel.local"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=security.get_password_hash("StrongDemoPassword123!"),
                full_name="Default Administrator",
                role=Role.ADMIN,
                is_active=True,
                email_verified=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Bootstrap: Created default demo admin account.")
        else:
            admin.is_active = True
            admin.email_verified = True
            db.commit()
    except Exception as e:
        logger.error(f"Bootstrap warning: {e}")
    finally:
        db.close()

@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    # Liveness check - very lightweight, just confirms the API is running
    return {
        "status": "ok",
        "service": "modelsentinel-api",
        "version": "0.1.0"
    }

@app.get("/ready")
def readiness_check():
    # Readiness check - ensures dependencies (DB, LLM) are up
    db_status = "unknown"
    db_engine = "unknown"
    is_ready = True
    try:
        db = SessionLocal()
        # Test connection
        db.execute(text("SELECT 1"))
        db_engine = db.bind.dialect.name
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        is_ready = False
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
            # Optional: Decide if misconfigured LLM means NOT READY. 
            # We'll allow it to be ready since LLM isn't strictly required for core telemetry.
    except Exception:
        provider_status = "unavailable"

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200 if is_ready else 503,
        content={
            "status": "ok" if is_ready else "error",
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
    )
