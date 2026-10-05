import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON

from app.db.base_class import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    source_type = Column(String)  # zip, public_git
    source_reference = Column(String) # URL or original filename
    default_branch = Column(String)
    current_commit = Column(String)
    status = Column(String, default="pending")  # pending, cloning, indexing, ready, failed
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    snapshots = relationship("RepositorySnapshot", back_populates="repository", cascade="all, delete-orphan")


class RepositorySnapshot(Base):
    __tablename__ = "repository_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_id = Column(String(36), ForeignKey("repositories.id"), nullable=False, index=True)
    commit_sha = Column(String, index=True)
    branch = Column(String)
    indexed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    file_count = Column(Integer, default=0)
    language_count = Column(Integer, default=0)
    status = Column(String, default="ready")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    repository = relationship("Repository", back_populates="snapshots")
    files = relationship("RepositoryFile", back_populates="snapshot", cascade="all, delete-orphan")
    dependencies = relationship("RepositoryDependency", back_populates="snapshot", cascade="all, delete-orphan")


class RepositoryFile(Base):
    __tablename__ = "repository_files"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_snapshot_id = Column(String(36), ForeignKey("repository_snapshots.id"), nullable=False, index=True)
    path = Column(String, index=True)
    language = Column(String)
    size_bytes = Column(Integer)
    sha256 = Column(String)
    line_count = Column(Integer)
    is_binary = Column(Boolean, default=False)
    indexed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    snapshot = relationship("RepositorySnapshot", back_populates="files")
    symbols = relationship("RepositorySymbol", back_populates="file", cascade="all, delete-orphan")


class RepositorySymbol(Base):
    __tablename__ = "repository_symbols"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_file_id = Column(String(36), ForeignKey("repository_files.id"), nullable=False, index=True)
    symbol_type = Column(String)  # module, class, function, method, import
    name = Column(String, index=True)
    qualified_name = Column(String, index=True)
    start_line = Column(Integer)
    end_line = Column(Integer)
    parent_symbol = Column(String, nullable=True)
    signature = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    file = relationship("RepositoryFile", back_populates="symbols")


class RepositoryDependency(Base):
    __tablename__ = "repository_dependencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_snapshot_id = Column(String(36), ForeignKey("repository_snapshots.id"), nullable=False, index=True)
    source_file_id = Column(String(36), ForeignKey("repository_files.id"), nullable=False, index=True)
    target_reference = Column(String)
    dependency_type = Column(String) # import
    resolved_target_file_id = Column(String(36), ForeignKey("repository_files.id"), nullable=True)

    snapshot = relationship("RepositorySnapshot", back_populates="dependencies")
    source_file = relationship("RepositoryFile", foreign_keys=[source_file_id])
    resolved_target_file = relationship("RepositoryFile", foreign_keys=[resolved_target_file_id])
