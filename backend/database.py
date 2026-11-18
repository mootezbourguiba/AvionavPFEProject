
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

# Define a stable absolute path for the SQLite database.
# This ensures the application always uses the same database,
# regardless of the directory from which it is launched.
DATABASE_PATH = Path(__file__).resolve().parent.parent / "avionics.db"

# Database URL from environment variable or default to the
# absolute SQLite database path.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_PATH.as_posix()}"
)

# Create SQLAlchemy engine.
# connect_args is needed only for SQLite.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class for session management.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base for model definitions.
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.

    This function is used as a FastAPI dependency to provide
    a database session for each request. The session is
    automatically closed after the request completes.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.

    This function should be called during application startup
    to ensure all tables are created. In production, use
    Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
