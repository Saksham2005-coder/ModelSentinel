from typing import Any
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from app.core.config import settings
from app.models.integration import WebhookEvent
import uuid
import datetime

router = APIRouter()

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    if not settings.MODELSENTINEL_GITHUB_WEBHOOK_SECRET:
        # In test mode without secret or misconfigured
        return False
    
    hash_object = hmac.new(
        settings.MODELSENTINEL_GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@router.post("/github/webhook")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    payload_body = await request.body()
    signature = request.headers.get("x-hub-signature-256")
    
    if not verify_github_signature(payload_body, signature):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")
        
    event_type = request.headers.get("x-github-event")
    delivery_id = request.headers.get("x-github-delivery")
    
    if not event_type or not delivery_id:
        raise HTTPException(status_code=400, detail="Missing GitHub event headers")
        
    # Check idempotency
    existing_event = db.query(WebhookEvent).filter(WebhookEvent.delivery_id == delivery_id).first()
    if existing_event:
        return {"status": "ok", "message": "Already processed", "delivery_id": delivery_id}
        
    payload = await request.json()
    
    # Store event
    webhook_event = WebhookEvent(
        id=str(uuid.uuid4()),
        provider="github",
        delivery_id=delivery_id,
        event_type=event_type,
        payload=payload,
        processing_status="PENDING",
        received_at=datetime.datetime.utcnow()
    )
    db.add(webhook_event)
    db.commit()
    db.refresh(webhook_event)
    
    # Process event asynchronously or synchronously based on the setup
    from app.services.webhook_processor import process_webhook_event
    try:
        process_webhook_event(db, webhook_event)
        webhook_event.processing_status = "PROCESSED"
        webhook_event.processed_at = datetime.datetime.utcnow()
    except Exception as e:
        webhook_event.processing_status = "FAILED"
        webhook_event.error_summary = str(e)
    
    db.commit()
    
    return {"status": "ok", "delivery_id": delivery_id, "processing_status": webhook_event.processing_status}

@router.get("")
def list_integrations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    from app.models.integration import Integration
    # Sync github status first
    ensure_github_integration(db)
    
    integrations = db.query(Integration).offset(skip).limit(limit).all()
    return integrations

@router.get("/github/status")
def get_github_status(
    db: Session = Depends(get_db)
) -> Any:
    from app.models.integration import Integration
    ensure_github_integration(db)
    integration = db.query(Integration).filter(Integration.provider == "github").first()
    return integration

def ensure_github_integration(db: Session):
    from app.models.integration import Integration
    integration = db.query(Integration).filter(Integration.provider == "github").first()
    has_token = bool(settings.MODELSENTINEL_GITHUB_TOKEN)
    status = "CONNECTED" if has_token else "DISCONNECTED"
    if not integration:
        integration = Integration(
            id=str(uuid.uuid4()),
            provider="github",
            type="repository",
            name="GitHub",
            status=status,
            config={"api_url": settings.MODELSENTINEL_GITHUB_API_URL}
        )
        db.add(integration)
        db.commit()
    else:
        if integration.status != status:
            integration.status = status
            db.commit()

@router.get("/webhooks")
def list_webhooks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    events = db.query(WebhookEvent).order_by(WebhookEvent.received_at.desc()).offset(skip).limit(limit).all()
    # Strip payload from list to save bandwidth and avoid leaking sensitive data
    return [
        {
            "id": e.id,
            "provider": e.provider,
            "delivery_id": e.delivery_id,
            "event_type": e.event_type,
            "processing_status": e.processing_status,
            "received_at": e.received_at,
            "error_summary": e.error_summary
        } for e in events
    ]
