from logging.config import fileConfig
from pathlib import Path

from src.shared.infrastructure.persistence.postgresql.configs.base import Base
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import make_url
from src.modules.auth.infrastructure.persistence.postgresql.models import *
from src.modules.internal_events.infrastructure.persistence.postgresql.models import *
from src.modules.journal.infrastructure.persistence.postgresql.models import *
from alembic import context
import os

from src.shared.config.settings import get_settings

_settings = get_settings()


raw_db_url = _settings.ALEMBIC_CONNECTION_STRING


if not raw_db_url:
    raise RuntimeError("DATABASE_URL não encontrada nas variáveis de ambiente!")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the configs_ file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", raw_db_url)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the configs_, defined by the needs of env.py,
# can be acquired:
# my_important_option = configs_.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_schemas=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
