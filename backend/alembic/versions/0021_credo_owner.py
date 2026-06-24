"""Add owner_id to credos — links a credo to the user account that owns it.

Nullable: NULL = platform-seeded / unowned credo, mirroring the `author_id`
convention on the beliefs / axes / issues library tables. This is the first
ownership column in the schema and the basis for the write/authorization
pattern (only a credo's owner may mutate it).

Revision ID: 0021
Revises: 0020
Create Date: 2026-06-15
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: Union[str, None] = "0020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "credos",
        sa.Column(
            "owner_id",
            sa.UUID,
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("credos_owner_id_idx", "credos", ["owner_id"])


def downgrade() -> None:
    op.drop_index("credos_owner_id_idx", table_name="credos")
    op.drop_column("credos", "owner_id")
