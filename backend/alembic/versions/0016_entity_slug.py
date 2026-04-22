"""Add slug column to entities for clean URL routing

Revision ID: 0016
Revises: 0015
Create Date: 2026-04-09
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("entities", sa.Column("slug", sa.Text, nullable=True))
    op.create_unique_constraint("entities_slug_key", "entities", ["slug"])
    op.create_index("entities_slug_idx", "entities", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("entities_slug_idx", table_name="entities")
    op.drop_constraint("entities_slug_key", "entities", type_="unique")
    op.drop_column("entities", "slug")
