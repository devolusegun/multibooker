import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# If you rely on .env for local dev:
from dotenv import load_dotenv
load_dotenv()  # This reads .env so we get DATABASE_URL

# Import your database config (engine, Base) from your code:
from app.database import engine, Base, DATABASE_URL

# Interpret the config file for Python logging.
# This sets up loggers using <alembic.ini>.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The target metadata is from your models' Base
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine.
    """
    # Instead of pulling from alembic.ini,
    # we directly use DATABASE_URL that we loaded from .env or environment
    url = DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is empty or not set.")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we create or reuse the Engine
    and associate a connection with the context.
    """
    # We can reuse the existing `engine` from app.database
    # OR create a new one, whichever you prefer:
    # connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
