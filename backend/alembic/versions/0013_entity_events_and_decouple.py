"""Decouple entities from credos; add entity_events

- entities loses credo_id and impact_score (becomes a global pool)
- credo_entities junction carries the per-context impact_score
- entity_events records specific documented actions

Revision ID: 0013
Revises: 0012
Create Date: 2026-04-09
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Junction: one entity can appear in many credos with different scores
    op.create_table(
        "credo_entities",
        sa.Column(
            "credo_id",
            sa.UUID,
            sa.ForeignKey("credos.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "entity_id",
            sa.UUID,
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("impact_score", sa.Integer, nullable=False),
        sa.CheckConstraint(
            "impact_score BETWEEN -100 AND 100",
            name="credo_entities_impact_score_check",
        ),
    )

    # Entity events: specific documented actions that justify an actor's score
    op.create_table(
        "entity_events",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "entity_id",
            sa.UUID,
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("event_date", sa.Date, nullable=True),
        sa.Column("metric_id", sa.Text, sa.ForeignKey("metrics.id"), nullable=True),
        sa.Column("event_impact_score", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "event_impact_score IS NULL OR event_impact_score BETWEEN -100 AND 100",
            name="entity_events_impact_score_check",
        ),
    )

    # Migrate existing credo_id + impact_score from entities into the junction table
    op.execute("""
        INSERT INTO credo_entities (credo_id, entity_id, impact_score)
        SELECT credo_id, id, impact_score
        FROM entities
        WHERE credo_id IS NOT NULL
    """)

    # Drop the now-redundant columns from entities
    op.drop_column("entities", "impact_score")
    op.drop_column("entities", "credo_id")

    # Seed entity events for the four existing actors
    op.execute("""
        INSERT INTO entity_events (entity_id, title, description, event_date, metric_id, event_impact_score)
        SELECT e.id, ev.title, ev.description, ev.event_date::date, ev.metric_id, ev.score
        FROM entities e
        JOIN (VALUES
            (
                'Illinois Housing Development Authority',
                'Issued $500M in affordable housing bonds',
                'New bond issuance allocated to fund affordable rental and ownership housing across Illinois, '
                'with a priority allocation to Cook County and collar counties.',
                '2022-09-15', 'median_home_price', 15
            ),
            (
                'Illinois Housing Development Authority',
                'Launched first-time homebuyer assistance program',
                'Program provides up to $10,000 in down payment and closing cost assistance to first-time buyers '
                'earning at or below 80% of area median income.',
                '2023-03-01', 'median_home_price', 20
            ),
            (
                'Chicago Community Land Trust',
                'Preserved 50 permanently affordable units in Logan Square',
                'Partnered with the City of Chicago to acquire and deed-restrict 50 homes '
                'threatened by speculative redevelopment pressure.',
                '2020-11-01', 'median_home_price', 15
            ),
            (
                'Chicago Community Land Trust',
                'Expanded resale formula to 25 municipalities',
                'Extended the shared equity model beyond Chicago city limits to 25 suburban municipalities, '
                'covering all seven counties tracked by this credo.',
                '2023-06-15', 'median_home_price', 10
            ),
            (
                'Invitation Homes',
                'Acquired 2,400 single-family homes across Chicago metro',
                'Bulk acquisition of owner-occupied homes converted to long-term rentals, '
                'removing a significant share of starter-home inventory from the for-sale market.',
                '2021-06-01', 'median_home_price', -25
            ),
            (
                'Invitation Homes',
                'Raised rents 8% across Illinois portfolio',
                'Rent increase applied uniformly across all Illinois-managed properties, '
                'ahead of wage growth and inflation, contributing to renter cost burden.',
                '2023-01-15', 'median_home_price', -20
            ),
            (
                'Related Midwest',
                'Received zoning variance for 500-unit luxury tower, minimal affordable units',
                'City Council approved a variance for a 500-unit development with a 5% affordable set-aside '
                '(25 units), significantly below the 20% recommended by housing advocates.',
                '2022-08-01', 'median_home_price', -15
            )
        ) AS ev(entity_name, title, description, event_date, metric_id, score)
        ON e.name = ev.entity_name
    """)


def downgrade() -> None:
    op.drop_table("entity_events")

    # Restore credo_id and impact_score columns to entities
    op.add_column("entities", sa.Column("credo_id", sa.UUID, sa.ForeignKey("credos.id"), nullable=True))
    op.add_column("entities", sa.Column("impact_score", sa.Integer, nullable=True))

    op.execute("""
        UPDATE entities e
        SET
            credo_id = ce.credo_id,
            impact_score = ce.impact_score
        FROM credo_entities ce
        WHERE ce.entity_id = e.id
    """)

    op.drop_table("credo_entities")
