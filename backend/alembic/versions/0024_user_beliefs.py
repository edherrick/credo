"""Add user_beliefs — a user's personal collection of endorsed beliefs.

Self-membership junction (mirrors credo_subscriptions): composite PK (user_id,
belief_id) makes saving idempotent; indexed on user_id for "beliefs I saved".
A saved belief can later be promoted into a credo the user owns (credo_beliefs).

Revision ID: 0024
Revises: 0023
Create Date: 2026-06-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0024"
down_revision: Union[str, None] = "0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_beliefs",
        sa.Column(
            "user_id",
            sa.UUID,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "belief_id",
            sa.UUID,
            sa.ForeignKey("beliefs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("user_beliefs_user_id_idx", "user_beliefs", ["user_id"])


def downgrade() -> None:
    op.drop_index("user_beliefs_user_id_idx", table_name="user_beliefs")
    op.drop_table("user_beliefs")
