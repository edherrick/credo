"""Create metric_values table

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-04
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "metric_values",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("metric_id", sa.Text, sa.ForeignKey("metrics.id"), nullable=False),
        sa.Column("geography_id", sa.Text, sa.ForeignKey("geographies.id"), nullable=False),
        sa.Column("value", sa.Numeric, nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("ingested_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("metric_id", "geography_id", "date", name="metric_values_unique"),
    )
    op.execute("""
        CREATE INDEX metric_values_lookup
        ON metric_values (metric_id, geography_id, date DESC)
    """)


def downgrade() -> None:
    op.drop_index("metric_values_lookup")
    op.drop_table("metric_values")
