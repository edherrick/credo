"""Add credo_subscriptions — a user follows a credo.

Self-membership junction (any user may follow any credo). Composite PK on
(user_id, credo_id) makes following idempotent. Indexed on user_id for the
"credos I follow" lookup. Distinct from owner_id / get_owned_credo, which is the
owner-scoped mutation pattern.

Revision ID: 0023
Revises: 0022
Create Date: 2026-06-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0023"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "credo_subscriptions",
        sa.Column(
            "user_id",
            sa.UUID,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "credo_id",
            sa.UUID,
            sa.ForeignKey("credos.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "credo_subscriptions_user_id_idx", "credo_subscriptions", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "credo_subscriptions_user_id_idx", table_name="credo_subscriptions"
    )
    op.drop_table("credo_subscriptions")
