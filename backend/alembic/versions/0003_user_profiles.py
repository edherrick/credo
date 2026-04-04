"""Create user_profiles table

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-04
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False),
        sa.Column("display_name", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
