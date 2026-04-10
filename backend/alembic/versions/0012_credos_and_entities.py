"""Add credos and entities tables; link agendas to credos

Revision ID: 0012
Revises: 0011
Create Date: 2026-04-09
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "credos",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.Text, nullable=False, unique=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_table(
        "entities",
        sa.Column("id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "credo_id",
            sa.UUID,
            sa.ForeignKey("credos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("impact_score", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "type IN ('politician', 'corporation', 'organization')",
            name="entities_type_check",
        ),
        sa.CheckConstraint(
            "impact_score BETWEEN -100 AND 100",
            name="entities_impact_score_check",
        ),
    )

    op.add_column(
        "agendas",
        sa.Column("credo_id", sa.UUID, sa.ForeignKey("credos.id"), nullable=True),
    )

    # Seed Ed's credo, link the existing agenda and seed actors
    op.execute("""
        WITH credo AS (
            INSERT INTO credos (username, title, description)
            VALUES (
                'ed',
                'Chicago Metro Housing Affordability',
                'A credo tracking housing affordability across the Chicago metro area. '
                'The goal is to lower median home prices to levels accessible to first-time buyers '
                'through evidence-backed policy.'
            )
            RETURNING id
        ),
        link_agenda AS (
            UPDATE agendas
            SET credo_id = (SELECT id FROM credo)
            WHERE metric_id = 'median_home_price'
        )
        INSERT INTO entities (credo_id, name, type, description, impact_score)
        SELECT
            c.id,
            e.name,
            e.type,
            e.description,
            e.score
        FROM (SELECT id FROM credo) c
        CROSS JOIN (VALUES
            (
                'Illinois Housing Development Authority',
                'organization',
                'State agency financing affordable housing development across Illinois through '
                'low-income housing tax credits, mortgage programs, and rental assistance.',
                75
            ),
            (
                'Chicago Community Land Trust',
                'organization',
                'Preserves permanently affordable homeownership in Chicago by retaining land '
                'ownership and selling homes at below-market prices with resale restrictions.',
                55
            ),
            (
                'Invitation Homes',
                'corporation',
                'Largest single-family rental company in the US. Acquisitions of owner-occupied '
                'homes at scale reduce supply available to first-time buyers and drive price appreciation.',
                -65
            ),
            (
                'Related Midwest',
                'corporation',
                'Major Chicago-area developer with a mixed record on affordable unit inclusion. '
                'Luxury-focused projects have drawn criticism for displacing lower-income residents.',
                -30
            )
        ) AS e(name, type, description, score)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM entities")
    op.execute("UPDATE agendas SET credo_id = NULL")
    op.drop_column("agendas", "credo_id")
    op.drop_table("entities")
    op.drop_table("credos")
