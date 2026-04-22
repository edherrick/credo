"""Add shared issues library for abstract policy areas

Adds:
  - issues: abstract policy areas (Housing Affordability, etc.)
  - issue_beliefs: junction — which beliefs an issue operationalises
  - agendas.issue_id: nullable FK linking a concrete agenda to an abstract issue

Seeds a canonical 'Housing Affordability' issue, links it to its foundational beliefs,
and links the existing median_home_price agenda to that issue.

Revision ID: 0020
Revises: 0019
Create Date: 2026-04-13
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0020"
down_revision: Union[str, None] = "0019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ISSUES_SEED = [
    {
        "title": "Housing Affordability",
        "description": (
            "The accessibility of housing at prices within reach of typical households, "
            "particularly first-time buyers and renters. Measured by price-to-income ratios, "
            "rental cost burden, and homeownership rates."
        ),
        "category": "housing",
    },
    {
        "title": "Voting Rights & Access",
        "description": (
            "The ability of eligible citizens to register, vote, and have their votes counted "
            "without undue burden. Encompasses registration rules, polling access, "
            "and protection from suppression."
        ),
        "category": "civic",
    },
    {
        "title": "Free Expression",
        "description": (
            "The right to speak, publish, and assemble without government interference. "
            "Includes press freedom, protest rights, and protection from prior restraint."
        ),
        "category": "rights",
    },
]


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. issues — shared library of abstract policy areas                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "issues",
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.Text, nullable=True),
        sa.Column("canonical", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("author_id", sa.UUID, sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "category IN ('housing', 'health', 'environment', 'rights', 'economy', 'civic')",
            name="issues_category_check",
        ),
    )

    for issue in ISSUES_SEED:
        op.execute(
            sa.text(
                "INSERT INTO issues (title, description, category, canonical) "
                "VALUES (:title, :description, :category, TRUE)"
            ).bindparams(
                title=issue["title"],
                description=issue["description"],
                category=issue["category"],
            )
        )

    # ------------------------------------------------------------------ #
    # 2. issue_beliefs — which beliefs an issue operationalises            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "issue_beliefs",
        sa.Column(
            "issue_id",
            sa.UUID,
            sa.ForeignKey("issues.id"),
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

    # Housing Affordability → its two foundational beliefs
    op.execute("""
        INSERT INTO issue_beliefs (issue_id, belief_id)
        SELECT i.id, b.id
        FROM issues i
        CROSS JOIN (
            SELECT id FROM beliefs
            WHERE title IN (
                'Access to safe housing is a human right',
                'Markets fail to deliver public goods without intervention'
            )
        ) b
        WHERE i.title = 'Housing Affordability'
    """)

    # Free Expression → freedom of speech belief
    op.execute("""
        INSERT INTO issue_beliefs (issue_id, belief_id)
        SELECT i.id, b.id
        FROM issues i
        JOIN beliefs b ON b.title = 'Freedom of speech and press'
        WHERE i.title = 'Free Expression'
    """)

    # Voting Rights → equal protection + consent of the governed
    op.execute("""
        INSERT INTO issue_beliefs (issue_id, belief_id)
        SELECT i.id, b.id
        FROM issues i
        CROSS JOIN (
            SELECT id FROM beliefs
            WHERE title IN (
                'Equal protection under the law',
                'Government derives its legitimate power from the consent of the governed'
            )
        ) b
        WHERE i.title = 'Voting Rights & Access'
    """)

    # ------------------------------------------------------------------ #
    # 3. agendas.issue_id — FK to the issues library                      #
    # ------------------------------------------------------------------ #
    op.add_column(
        "agendas",
        sa.Column(
            "issue_id",
            sa.UUID,
            sa.ForeignKey("issues.id"),
            nullable=True,
        ),
    )

    # Link the existing housing agenda to the Housing Affordability issue
    op.execute("""
        UPDATE agendas
        SET issue_id = (SELECT id FROM issues WHERE title = 'Housing Affordability')
        WHERE metric_id = 'median_home_price'
    """)


def downgrade() -> None:
    op.drop_column("agendas", "issue_id")
    op.drop_table("issue_beliefs")
    op.drop_table("issues")
