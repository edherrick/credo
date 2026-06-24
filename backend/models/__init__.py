"""ORM models package.

Importing this package imports every model module, which registers all tables on
``Base.metadata``. Alembic's ``target_metadata`` points at that metadata so
``alembic check`` / ``--autogenerate`` can detect model↔DB drift. ``Base`` is
re-exported here as the canonical import location.
"""
from models.user import Base

# Import each module so its tables attach to Base.metadata. Order doesn't matter;
# all depend only on `Base` from models.user.
from . import agenda, credo, geography, metric  # noqa: F401,E402

__all__ = ["Base"]
