
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declared_attr

from backend.database import Base


def _utcnow():
    """Return the current UTC time as a timezone-naive datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BaseModel(Base):
    """
    Base model class for all database models.

    Provides common attributes:
    - id: Primary key
    - created_at: Timestamp for record creation
    - updated_at: Timestamp for last modification

    Python-side defaults ensure timestamps are supplied by SQLAlchemy
    even when the existing database schema has no server defaults.
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        """
        Automatically generate table name from class name.
        """
        return cls.__name__.lower()

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    created_at = Column(
        DateTime,
        default=_utcnow,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=_utcnow,
        onupdate=_utcnow,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
