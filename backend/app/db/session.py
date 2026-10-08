from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Default to SQLite if TESTING or DATABASE_URL indicates sqlite
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI, 
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_size=20,           # Keep up to 20 persistent connections
        max_overflow=10,        # Allow up to 10 extra temporary connections during bursts
        pool_timeout=30,        # Wait up to 30 seconds for an available connection
        pool_recycle=1800,      # Recycle connections every 30 minutes to prevent stale/dropped connections
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
