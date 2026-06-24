import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from models import Base

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"].replace("+asyncpg", ""))

target_metadata = Base.metadata


def include_object(obj, name, type_, reflected, compare_to):
    """Scope drift detection to the tables/columns we actually model.

    The PostGIS image ships dozens of extension tables (spatial_ref_sys, the
    tiger geocoder, topology); ignore anything not in our metadata. Indexes and
    unique constraints are added by hand in migrations rather than declared on
    the models, so they're excluded too; column types aren't compared (the schema
    standardizes on TEXT while fastapi-users' base declares String(n)). The guard
    focuses on table + column presence/nullability + FK drift.
    """
    if type_ == "table" and reflected and name not in target_metadata.tables:
        return False
    if type_ in ("index", "unique_constraint"):
        return False
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_object=include_object,
        compare_type=False,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
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
            compare_type=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
