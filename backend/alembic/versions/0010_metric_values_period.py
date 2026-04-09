"""Rename metric_values.date to period_start, add period_end

Revision ID: 0010
Revises: 0009
Create Date: 2026-04-07
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old unique constraint and index (both reference 'date')
    op.drop_constraint("metric_values_unique", "metric_values")
    op.drop_index("metric_values_lookup")

    # Rename date → period_start
    op.alter_column("metric_values", "date", new_column_name="period_start")

    # Add optional period_end (null = point-in-time)
    op.add_column("metric_values", sa.Column("period_end", sa.Date, nullable=True))

    # Recreate constraint and index on period_start
    op.create_unique_constraint(
        "metric_values_unique",
        "metric_values",
        ["metric_id", "geography_id", "period_start"],
    )
    op.execute("""
        CREATE INDEX metric_values_lookup
        ON metric_values (metric_id, geography_id, period_start DESC)
    """)


def downgrade() -> None:
    op.drop_index("metric_values_lookup")
    op.drop_constraint("metric_values_unique", "metric_values")
    op.drop_column("metric_values", "period_end")
    op.alter_column("metric_values", "period_start", new_column_name="date")
    op.create_unique_constraint(
        "metric_values_unique",
        "metric_values",
        ["metric_id", "geography_id", "date"],
    )
    op.execute("""
        CREATE INDEX metric_values_lookup
        ON metric_values (metric_id, geography_id, date DESC)
    """)
