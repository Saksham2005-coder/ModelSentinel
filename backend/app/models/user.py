import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum
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
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
