from sqlmodel import SQLModel
from models.db_setup import engine  # Import your SQLModel engine
from logging.config import fileConfig

from alembic import context

# Alembic Config object for accessing .ini settings
config = context.config

# Set up Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLModel metadata as target_metadata
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario, an Engine is used, and a connection is associated with the context.
    """
    with engine.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Check mode and execute the appropriate migration function
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
