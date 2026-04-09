"""Seed Chicago-area collar county geographies and metric values

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-04
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Metadata rows — boundaries loaded separately via scripts/load_chicago_counties.py
    op.execute("""
        INSERT INTO geographies (id, name, state_fips, geo_type) VALUES
            ('17043', 'DuPage County, IL',  '17', 'county'),
            ('17097', 'Lake County, IL',    '17', 'county'),
            ('17197', 'Will County, IL',    '17', 'county'),
            ('17089', 'Kane County, IL',    '17', 'county'),
            ('17111', 'McHenry County, IL', '17', 'county'),
            ('17093', 'Kendall County, IL', '17', 'county')
        ON CONFLICT (id) DO NOTHING
    """)

    # Approximate median home prices 2020-2024 (USD)
    # DuPage is the priciest collar county; Will/McHenry the most affordable.
    # Values intentionally span the full choropleth scale (~$240k – $430k).
    op.execute("""
        INSERT INTO metric_values (metric_id, geography_id, value, date) VALUES
            ('median_home_price', '17043', 355000, '2020-01-01'),
            ('median_home_price', '17043', 375000, '2021-01-01'),
            ('median_home_price', '17043', 395000, '2022-01-01'),
            ('median_home_price', '17043', 415000, '2023-01-01'),
            ('median_home_price', '17043', 428000, '2024-01-01'),

            ('median_home_price', '17097', 310000, '2020-01-01'),
            ('median_home_price', '17097', 330000, '2021-01-01'),
            ('median_home_price', '17097', 345000, '2022-01-01'),
            ('median_home_price', '17097', 365000, '2023-01-01'),
            ('median_home_price', '17097', 385000, '2024-01-01'),

            ('median_home_price', '17197', 240000, '2020-01-01'),
            ('median_home_price', '17197', 258000, '2021-01-01'),
            ('median_home_price', '17197', 272000, '2022-01-01'),
            ('median_home_price', '17197', 289000, '2023-01-01'),
            ('median_home_price', '17197', 305000, '2024-01-01'),

            ('median_home_price', '17089', 265000, '2020-01-01'),
            ('median_home_price', '17089', 280000, '2021-01-01'),
            ('median_home_price', '17089', 295000, '2022-01-01'),
            ('median_home_price', '17089', 310000, '2023-01-01'),
            ('median_home_price', '17089', 325000, '2024-01-01'),

            ('median_home_price', '17111', 245000, '2020-01-01'),
            ('median_home_price', '17111', 262000, '2021-01-01'),
            ('median_home_price', '17111', 278000, '2022-01-01'),
            ('median_home_price', '17111', 295000, '2023-01-01'),
            ('median_home_price', '17111', 312000, '2024-01-01'),

            ('median_home_price', '17093', 280000, '2020-01-01'),
            ('median_home_price', '17093', 300000, '2021-01-01'),
            ('median_home_price', '17093', 320000, '2022-01-01'),
            ('median_home_price', '17093', 340000, '2023-01-01'),
            ('median_home_price', '17093', 358000, '2024-01-01')
        ON CONFLICT ON CONSTRAINT metric_values_unique DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM metric_values
        WHERE geography_id IN ('17043','17097','17197','17089','17111','17093')
    """)
    op.execute("""
        DELETE FROM geographies
        WHERE id IN ('17043','17097','17197','17089','17111','17093')
    """)
