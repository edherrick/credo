"""Create agendas table and seed Cook County agenda

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-04
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agendas",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("metric_id", sa.Text, sa.ForeignKey("metrics.id"), nullable=True),
        sa.Column("geography_id", sa.Text, sa.ForeignKey("geographies.id"), nullable=True),
        sa.Column("direction", sa.Text, nullable=False),
        sa.Column("target_value", sa.Numeric, nullable=True),
        sa.Column("target_date", sa.Date, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint("direction IN ('lower', 'raise')", name="agendas_direction_check"),
        sa.CheckConstraint("status IN ('active', 'draft', 'achieved', 'abandoned')", name="agendas_status_check"),
    )
    # Seed row depends on geographies being populated (run load_cook_county.py first)
    # Inserted by 0009 after geography seed


def downgrade() -> None:
    op.drop_table("agendas")
