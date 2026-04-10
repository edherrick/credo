"""Replace agendas.geography_id with agenda_geographies junction table

Revision ID: 0011
Revises: 0010
Create Date: 2026-04-09
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agenda_geographies",
        sa.Column(
            "agenda_id",
            sa.UUID,
            sa.ForeignKey("agendas.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "geography_id",
            sa.Text,
            sa.ForeignKey("geographies.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
    )

    # Migrate existing geography_id values into the junction table
    op.execute("""
        INSERT INTO agenda_geographies (agenda_id, geography_id)
        SELECT id, geography_id FROM agendas
        WHERE geography_id IS NOT NULL
    """)

    # Expand the Cook County housing agenda to cover all Chicago-area counties
    op.execute("""
        INSERT INTO agenda_geographies (agenda_id, geography_id)
        SELECT a.id, g.id
        FROM agendas a
        CROSS JOIN (
            SELECT id FROM geographies
            WHERE id IN ('17043', '17097', '17197', '17089', '17111', '17093')
        ) g
        WHERE a.metric_id = 'median_home_price'
        ON CONFLICT DO NOTHING
    """)

    # Retitle the agenda now that it covers the full metro
    op.execute("""
        UPDATE agendas
        SET title = 'Lower Median Home Price Across Chicago Metro'
        WHERE metric_id = 'median_home_price'
    """)

    # Drop the now-redundant column (PostgreSQL drops the FK constraint automatically)
    op.drop_column("agendas", "geography_id")


def downgrade() -> None:
    op.add_column(
        "agendas",
        sa.Column("geography_id", sa.Text, sa.ForeignKey("geographies.id"), nullable=True),
    )
    # Restore geography_id as the first geography from the junction table
    op.execute("""
        UPDATE agendas a
        SET geography_id = (
            SELECT geography_id FROM agenda_geographies ag
            WHERE ag.agenda_id = a.id
            ORDER BY geography_id
            LIMIT 1
        )
    """)
    op.drop_table("agenda_geographies")
