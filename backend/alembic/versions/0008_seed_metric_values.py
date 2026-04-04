"""Seed dummy Cook County metric values to unblock UI

Revision ID: 0008
Revises: 0007
Create Date: 2026-04-04

NOTE: Cook County boundary (FIPS 17031) must be loaded first via:
    python scripts/load_cook_county.py
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dummy values to render the choropleth while real Zillow data is sourced
    op.execute("""
        INSERT INTO metric_values (metric_id, geography_id, value, date) VALUES
            ('median_home_price', '17031', 280000, '2020-01-01'),
            ('median_home_price', '17031', 290000, '2021-01-01'),
            ('median_home_price', '17031', 295000, '2022-01-01'),
            ('median_home_price', '17031', 315000, '2023-01-01'),
            ('median_home_price', '17031', 331000, '2024-01-01')
        ON CONFLICT ON CONSTRAINT metric_values_unique DO NOTHING
    """)
    op.execute("""
        INSERT INTO agendas (title, metric_id, geography_id, direction, target_value, target_date)
        VALUES (
            'Lower Median Home Price in Cook County for First-Time Buyers',
            'median_home_price',
            '17031',
            'lower',
            280000,
            '2030-01-01'
        )
    """)


def downgrade() -> None:
    op.execute("DELETE FROM agendas WHERE geography_id = '17031'")
    op.execute("DELETE FROM metric_values WHERE geography_id = '17031'")
