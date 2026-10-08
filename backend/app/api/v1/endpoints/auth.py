from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.api import deps
from app.core import security
from app.models.user import User, Role
from app.services import audit_service

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

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

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
        role=Role.VIEWER  # Force normal registrations to VIEWER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS"
    )
    
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        # We can record failed login attempts
        if user:
            audit_service.record_event(
                db=db, actor_id=user.id, actor_type="USER", action="USER_LOGIN", 
                resource_type="AUTH", resource_id="token", result="FAILED"
            )
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = security.create_access_token(user.id)
    
    audit_service.record_event(
        db=db,
        actor_id=user.id,
        actor_type="USER",
        action="USER_LOGIN",
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
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    audit_service.record_event(
        db=db,
        actor_id=current_user.id,
        actor_type="USER",
        action="USER_LOGOUT",
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
