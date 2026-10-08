import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey
import sqlalchemy
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    ML_ENGINEER = "ML_ENGINEER"
    REVIEWER = "REVIEWER"
    VIEWER = "VIEWER"
    INTEGRATION = "INTEGRATION"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    verification_tokens = relationship("VerificationToken", back_populates="user", cascade="all, delete-orphan")

class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, sqlalchemy.ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="verification_tokens")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String, unique=True, index=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
