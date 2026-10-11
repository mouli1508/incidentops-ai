
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import settings
from app.db.base import Base
import app.db.models  # Register ORM models


# Alembic configuration
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Generate SQL without connecting to the database."""

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()



def run_migrations_online():
    print("[1] Creating database engine...", flush=True)

    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
        connect_args={"connect_timeout": 5},
    )

    print("[2] Connecting to PostgreSQL...", flush=True)

    with connectable.connect() as connection:
        print("[3] Connected successfully!", flush=True)

        print("[4] Configuring Alembic...", flush=True)

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        print("[5] Starting schema comparison...", flush=True)

        with context.begin_transaction():
            context.run_migrations()

        print("[6] Migration processing completed!", flush=True)

    connectable.dispose()



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
