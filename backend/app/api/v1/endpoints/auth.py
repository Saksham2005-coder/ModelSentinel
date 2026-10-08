from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.api import deps
from app.core import security
from app.models.user import User, Role, BlacklistedToken
from app.services import audit_service, email_service
import datetime

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None
    role: Role = Role.VIEWER

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: Role
    is_active: bool
    email_verified: bool
    dev_verification_token: str = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class VerifyEmailRequest(BaseModel):
    token: str

class ResendEmailRequest(BaseModel):
    email: EmailStr

@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=Role.VIEWER,  # Force normal registrations to VIEWER
        email_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = email_service.create_verification_token(db, user)
    email_service.send_verification_email(user.email, token)
    
    # If in development, return the token so the UI can show the link
    import os
    if os.getenv("EMAIL_PROVIDER", "console") == "console":
        user.dev_verification_token = token
    
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS"
    )
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="EMAIL_VERIFICATION_REQUESTED",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS"
    )
    
    return user

@router.post("/verify-email")
def verify_email(
    req: VerifyEmailRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    user = email_service.verify_token(db, req.token)
    if not user:
        # We don't have user context here easily for audit on failure, but it's a failed attempt
        raise HTTPException(status_code=400, detail="That verification link is invalid or has expired.")
        
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="EMAIL_VERIFIED",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS"
    )
    return {"status": "Email verified successfully."}

@router.post("/resend-verification")
def resend_verification(
    req: ResendEmailRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    # Deterministic rate limiting / cooldown could go here
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Don't expose that the email doesn't exist
        return {"status": "If an account exists, a verification email has been sent."}
        
    if user.email_verified:
        return {"status": "If an account exists, a verification email has been sent."}
        
    token = email_service.create_verification_token(db, user)
    email_service.send_verification_email(user.email, token)
    
    import os
    if os.getenv("EMAIL_PROVIDER", "console") == "console":
        # In dev mode, we could return it, but resend endpoint response is fixed.
        # Let's change the response for dev mode.
        return {"status": "If an account exists, a verification email has been sent.", "dev_verification_token": token}
    
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="EMAIL_VERIFICATION_RESENT",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS"
    )
    
    return {"status": "If an account exists, a verification email has been sent."}

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        if user:
            audit_service.record_event(
                db=db, actor_id=user.id, actor_type="USER", action="LOGIN_FAILED", 
                resource_type="AUTH", resource_id="token", result="FAILED"
            )
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    elif not user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please verify your email before signing in.")

    access_token = security.create_access_token(user.id)
    
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="LOGIN_SUCCESS",
        resource_type="AUTH",
        resource_id="token",
        result="SUCCESS"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    token: str = Depends(deps.oauth2_scheme),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Invalidate token
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    blacklisted_token = BlacklistedToken(
        token=token,
        expires_at=expires_at
    )
    db.add(blacklisted_token)
    db.commit()

    audit_service.record_event(
        db=db,
        actor_id=current_user.id,
        actor_type="USER",
        action="LOGOUT",
        resource_type="AUTH",
        resource_id="token",
        result="SUCCESS"
    )
    return {"status": "ok"}

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    return current_user
