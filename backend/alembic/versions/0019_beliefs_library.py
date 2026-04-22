"""Add shared beliefs library for founding principles

Adds:
  - beliefs: canonical founding principles and philosophical axioms
  - credo_beliefs: junction — which beliefs a credo holds (display order + notes)
  - agenda_beliefs: junction — which beliefs an agenda operationalises

Seeds 7 canonical beliefs (constitutional and philosophical).
Links two housing-related beliefs to the 'ed' credo and to the housing agenda.

Revision ID: 0019
Revises: 0018
Create Date: 2026-04-13
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: Union[str, None] = "0018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BELIEFS_SEED = [
    {
        "title": "Access to safe housing is a human right",
        "statement": (
            "Access to safe, stable, and affordable housing is a fundamental human right "
            "that enables full participation in society and protection from exploitation."
        ),
        "category": "rights",
        "source": None,
    },
    {
        "title": "Markets fail to deliver public goods without intervention",
        "statement": (
            "Unregulated markets systematically under-produce goods with positive externalities "
            "and over-produce goods with negative ones. Public intervention is necessary to "
            "correct these failures and ensure broadly shared outcomes."
        ),
        "category": "economic",
        "source": None,
    },
    {
        "title": "All people are created equal and deserve equal opportunity",
        "statement": (
            "Every person is endowed with equal inherent dignity and is entitled to fair "
            "opportunity to pursue their own flourishing, unconstrained by arbitrary circumstances of birth."
        ),
        "category": "philosophical",
        "source": "Declaration of Independence",
    },
    {
        "title": "Equal protection under the law",
        "statement": (
            "No state shall deny to any person within its jurisdiction the equal protection "
            "of the laws. Government may not arbitrarily discriminate among persons."
        ),
        "category": "legal",
        "source": "14th Amendment",
    },
    {
        "title": "Freedom of speech and press",
        "statement": (
            "Congress shall make no law abridging the freedom of speech, or of the press. "
            "Open inquiry and the free exchange of ideas are preconditions of self-governance."
        ),
        "category": "legal",
        "source": "1st Amendment",
    },
    {
        "title": "Government derives its legitimate power from the consent of the governed",
        "statement": (
            "Just governments are instituted among people and derive their legitimate authority "
            "from the ongoing, informed consent of those they govern. Accountability to the "
            "governed is not optional — it is the foundation of legitimacy."
        ),
        "category": "philosophical",
        "source": "Declaration of Independence",
    },
    {
        "title": "No person shall be deprived of life, liberty, or property without due process",
        "statement": (
            "The state may not deprive any person of life, liberty, or property without due "
            "process of law. Procedural fairness is not a technicality — it is a constraint "
            "on arbitrary power."
        ),
        "category": "legal",
        "source": "5th Amendment",
    },
]


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. beliefs — shared library of foundational principles               #
    # ------------------------------------------------------------------ #
    op.create_table(
        "beliefs",
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("statement", sa.Text, nullable=False),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("source", sa.Text, nullable=True),
        sa.Column("canonical", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("author_id", sa.UUID, sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "category IN ('philosophical', 'legal', 'economic', 'civic', 'rights')",
            name="beliefs_category_check",
        ),
    )

    op.create_index("beliefs_category_idx", "beliefs", ["category"])
    op.create_index(
        "beliefs_canonical_idx",
        "beliefs",
        ["canonical"],
        postgresql_where=sa.text("canonical = TRUE"),
    )

    for b in BELIEFS_SEED:
        op.execute(
            sa.text(
                "INSERT INTO beliefs (title, statement, category, source, canonical) "
                "VALUES (:title, :statement, :category, :source, TRUE)"
            ).bindparams(
                title=b["title"],
                statement=b["statement"],
                category=b["category"],
                source=b["source"],
            )
        )

    # ------------------------------------------------------------------ #
    # 2. credo_beliefs — which beliefs a credo holds                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "credo_beliefs",
        sa.Column(
            "credo_id",
            sa.UUID,
            sa.ForeignKey("credos.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "belief_id",
            sa.UUID,
            sa.ForeignKey("beliefs.id"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("display_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Link two housing-related beliefs to Ed's credo
    op.execute("""
        INSERT INTO credo_beliefs (credo_id, belief_id, display_order)
        SELECT c.id, b.id, b.ord
        FROM credos c
        CROSS JOIN (
            SELECT id, 1 AS ord
            FROM beliefs
            WHERE title = 'Access to safe housing is a human right'
            UNION ALL
            SELECT id, 2 AS ord
            FROM beliefs
            WHERE title = 'Markets fail to deliver public goods without intervention'
        ) b
        WHERE c.username = 'ed'
    """)

    # ------------------------------------------------------------------ #
    # 3. agenda_beliefs — which beliefs an agenda operationalises          #
    # ------------------------------------------------------------------ #
    op.create_table(
        "agenda_beliefs",
        sa.Column(
            "agenda_id",
            sa.UUID,
            sa.ForeignKey("agendas.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "belief_id",
            sa.UUID,
            sa.ForeignKey("beliefs.id"),
            primary_key=True,
            nullable=False,
        ),
    )

    # Link the existing housing agenda to both housing beliefs
    op.execute("""
        INSERT INTO agenda_beliefs (agenda_id, belief_id)
        SELECT a.id, b.id
        FROM agendas a
        CROSS JOIN (
            SELECT id FROM beliefs
            WHERE title IN (
                'Access to safe housing is a human right',
                'Markets fail to deliver public goods without intervention'
            )
        ) b
        WHERE a.metric_id = 'median_home_price'
    """)


def downgrade() -> None:
    op.drop_table("agenda_beliefs")
    op.drop_table("credo_beliefs")
    op.drop_index("beliefs_canonical_idx", table_name="beliefs")
    op.drop_index("beliefs_category_idx", table_name="beliefs")
    op.drop_table("beliefs")
