"""Create metrics table and seed median_home_price

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-04
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "metrics",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("unit", sa.Text, nullable=False),
        sa.Column("provider_id", sa.Text, nullable=False, server_default="platform"),
        sa.Column("data_source", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("""
        INSERT INTO metrics (id, display_name, description, unit, provider_id, data_source)
        VALUES (
            'median_home_price',
            'Median Home Price',
            'Median sale price of residential properties in the geography',
            'USD',
            'platform',
            'zillow_zhvi'
        )
    """)


def downgrade() -> None:
    op.drop_table("metrics")
