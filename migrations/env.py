from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# load per-env dotenv files so Alembic sees your secrets
import os
from pathlib import Path
from dotenv import load_dotenv

# load .flaskenv to get APP_ENV, then the matching .env.{env}
load_dotenv(".flaskenv")  # contains APP_ENV
env = (os.getenv("APP_ENV") or "development").lower()
load_dotenv(Path(f".env.{env}"), override=True)

os.environ["ALEMBIC_RUNNING"] = "1"

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# set sqlalchemy.url from env at runtime
db_url = os.getenv("SUPABASE_DB_URL")
if not db_url:
    raise RuntimeError("SUPABASE_DB_URL is not set")
config.set_main_option("sqlalchemy.url", db_url)

print(f"[alembic] APP_ENV={env}  url_driver={db_url.split('://',1)[0]}")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from app.models import Base

# from app.services.db import Base
# from app.models.models import *
from app.models import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Skip Supabase/pg system schemas
EXCLUDE_SCHEMAS = {"pgbouncer", "pg_catalog", "information_schema", "auth", "storage", "realtime"}

def include_object(object, name, type_, reflected, compare_to):
    # Skip everything in excluded schemas
    schema = getattr(object, "schema", None)
    if schema in EXCLUDE_SCHEMAS:
        return False
    return True


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
        include_object=include_object,         
        compare_type=True,                     
        compare_server_default=True,           
        # render_nullability=True,             # optional but handy
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
            include_object=include_object,    
            compare_type=True,                 
            compare_server_default=True,       
            # render_nullability=True,         # optional
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
