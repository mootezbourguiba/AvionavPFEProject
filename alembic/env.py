
from logging.config import fileConfig
import sys
import os

from alembic import context

# Add the project root to the Python path.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import the application's database configuration and engine.
from backend.database import Base, DATABASE_URL, engine

# Import models so that all tables are registered in Base.metadata.
from backend.models.user import User
from backend.models.telemetry import TelemetryReading
from backend.models.base import BaseModel

# Alembic configuration object.
config = context.config

# Configure logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Always use the same database URL as the application.
# Escape percent signs for ConfigParser compatibility.
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)

# Metadata used by Alembic for migrations.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations without creating a database connection.
    Uses the same database URL as the application.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations using the application's existing SQLAlchemy engine.
    This guarantees that Alembic and FastAPI use the same database.
    """
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
