from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.session import SessionLocal
from app.models.user import User, BlacklistedToken
from app.core import security
from app.core.rbac import has_permission

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{security.settings.API_V1_STR}/auth/login" if hasattr(security, 'settings') else "/api/v1/auth/login"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        # Check blacklist
        is_blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated",
            )
            
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not current_user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please verify your email address")
    return current_user

class RequirePermissions:
    def __init__(self, permissions: List[str]):
        self.permissions = permissions

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        for perm in self.permissions:
            if not has_permission(current_user.role, perm):
                # We also want to record an audit event for authorization failure, but that's better done centrally.
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions: {perm}"
                )
        return current_user
