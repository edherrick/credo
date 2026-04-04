"""Create geographies table

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-04
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "geographies",
        sa.Column("id", sa.Text, primary_key=True),  # FIPS code e.g. '17031'
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("state_fips", sa.Text, nullable=False),
        sa.Column("geo_type", sa.Text, nullable=False, server_default="county"),
        sa.Column("boundary", Geometry("MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.execute("CREATE INDEX geographies_boundary_gist ON geographies USING GIST (boundary)")
    # Seed Cook County metadata now; boundary is loaded separately via scripts/load_cook_county.py
    op.execute("""
        INSERT INTO geographies (id, name, state_fips, geo_type)
        VALUES ('17031', 'Cook County, IL', '17', 'county')
        ON CONFLICT (id) DO NOTHING
    """)


def downgrade() -> None:
    op.drop_index("geographies_boundary_gist")
    op.drop_table("geographies")
