"""Create users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-04
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text, unique=True, nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_superuser", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    op.drop_table("users")
