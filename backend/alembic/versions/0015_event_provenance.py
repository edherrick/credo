"""Add provenance fields to entities and entity_events for crawler/import support

Adds:
  entities.wikidata_id        — stable cross-source identifier for entity resolution
  entity_events.source_url    — URL of the article/document the event was extracted from
  entity_events.source_type   — 'manual' | 'wikipedia' | 'news' | 'government'
  entity_events.confidence    — extraction confidence (1.0 for human-authored)
  entity_events.reviewed      — whether a human has approved the event for display

All new columns are nullable or have defaults compatible with existing rows, so no
data migration is required.

Revision ID: 0015
Revises: 0014
Create Date: 2026-04-09
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SOURCE_TYPES = ("manual", "wikipedia", "news", "government")


def upgrade() -> None:
    # Entity: stable external identifier for cross-source resolution
    op.add_column("entities", sa.Column("wikidata_id", sa.Text, nullable=True, unique=True))

    # Entity events: provenance metadata for crawler-ingested events
    op.add_column("entity_events", sa.Column("source_url", sa.Text, nullable=True))
    op.add_column(
        "entity_events",
        sa.Column("source_type", sa.Text, nullable=False, server_default="manual"),
    )
    op.add_column(
        "entity_events",
        sa.Column(
            "confidence",
            sa.Numeric(precision=4, scale=3),
            nullable=False,
            server_default="1.000",
        ),
    )
    op.add_column(
        "entity_events",
        sa.Column("reviewed", sa.Boolean, nullable=False, server_default="true"),
    )

    op.create_check_constraint(
        "entity_events_source_type_check",
        "entity_events",
        f"source_type IN {SOURCE_TYPES}",
    )


def downgrade() -> None:
    op.drop_constraint("entity_events_source_type_check", "entity_events")
    op.drop_column("entity_events", "reviewed")
    op.drop_column("entity_events", "confidence")
    op.drop_column("entity_events", "source_type")
    op.drop_column("entity_events", "source_url")
    op.drop_column("entities", "wikidata_id")
