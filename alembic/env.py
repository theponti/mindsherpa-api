from dotenv import load_dotenv

load_dotenv()

from alembic import context  # noqa: E402
from logging.config import fileConfig  # noqa: E402
import os  # noqa: E402

from sqlalchemy import engine_from_config  # noqa: E402
from sqlalchemy import pool  # noqa: E402

from src.data.db import Base  # noqa: E402
from src.data.models.action import Action
from src.data.models.chat import Chat, Message
from src.data.models.context import Context, SystemState
from src.data.models.entity import Entity
from src.data.models.entity_memory import EntityMemory
from src.data.models.focus import Focus
from src.data.models.memory import Memory
from src.data.models.memory_tags import memory_tags
from src.data.models.note import Note
from src.data.models.note_tags import note_tags
from src.data.models.queue import Queue
from src.data.models.relationship import Relationship
from src.data.models.tag import Tag
from src.data.models.user import User, Profile


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = os.getenv("DATABASE_URL")
    if url is None:
        raise ValueError("DATABASE_URL environment variable is not set.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # Read the database URL from the environment variable
    url = os.getenv("DATABASE_URL")
    if url is None:
        raise ValueError("DATABASE_URL environment variable is not set.")

    # Override the URL in the alembic.ini file
    config.set_main_option("sqlalchemy.url", url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
