"""Enable uuid-ossp and postgis extensions

Revision ID: 0001
Revises:
Create Date: 2026-04-04
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def downgrade() -> None:
    pass  # never drop extensions — other objects may depend on them
