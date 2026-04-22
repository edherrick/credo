"""Add shared axes library for multi-axis entity scoring

Adds:
  - axes: canonical evaluation dimensions (housing, environmental, etc.)
  - credo_axes: junction — which axes a credo uses, with relative weight
  - credo_entity_scores: per-axis entity scores; replaces credo_entities.impact_score
    in Phase 2+ (the old column is kept for backward compatibility until stance radar ships)

Seeds 7 canonical axes and links the 'housing' axis to the 'ed' credo.

Revision ID: 0018
Revises: 0017
Create Date: 2026-04-13
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


AXES_SEED = [
    ("housing",        "Housing Affordability",    "economic",     True),
    ("environmental",  "Environmental Policy",     "environmental", True),
    ("civil-liberties","Civil Liberties",          "civic",        True),
    ("gun-regulation", "Gun Regulation",           "civic",        True),
    ("labor",          "Labor & Workers Rights",   "economic",     True),
    ("healthcare",     "Healthcare Access",        "social",       True),
    ("education",      "Education",                "social",       True),
]


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. axes — shared library of evaluation dimensions                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "axes",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("label", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("family", sa.Text, nullable=False),
        sa.Column("canonical", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("author_id", sa.UUID, sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "family IN ('economic', 'social', 'civic', 'environmental')",
            name="axes_family_check",
        ),
    )

    for axis_id, label, family, canonical in AXES_SEED:
        op.execute(
            sa.text(
                "INSERT INTO axes (id, label, family, canonical) "
                "VALUES (:id, :label, :family, :canonical)"
            ).bindparams(id=axis_id, label=label, family=family, canonical=canonical)
        )

    # ------------------------------------------------------------------ #
    # 2. credo_axes — which axes a credo evaluates entities on             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "credo_axes",
        sa.Column(
            "credo_id",
            sa.UUID,
            sa.ForeignKey("credos.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "axis_id",
            sa.Text,
            sa.ForeignKey("axes.id"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("weight", sa.Integer, nullable=False, server_default=sa.text("1")),
    )

    # Link the 'housing' axis to Ed's credo
    op.execute("""
        INSERT INTO credo_axes (credo_id, axis_id, weight)
        SELECT id, 'housing', 1
        FROM credos
        WHERE username = 'ed'
    """)

    # ------------------------------------------------------------------ #
    # 3. credo_entity_scores — per-axis entity scores                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "credo_entity_scores",
        sa.Column(
            "credo_id",
            sa.UUID,
            sa.ForeignKey("credos.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "entity_id",
            sa.UUID,
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "axis_id",
            sa.Text,
            sa.ForeignKey("axes.id"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "score BETWEEN -100 AND 100",
            name="credo_entity_scores_range_check",
        ),
    )

    op.create_index(
        "credo_entity_scores_entity_idx",
        "credo_entity_scores",
        ["entity_id"],
    )
    op.create_index(
        "credo_entity_scores_axis_idx",
        "credo_entity_scores",
        ["axis_id"],
    )


def downgrade() -> None:
    op.drop_index("credo_entity_scores_axis_idx", table_name="credo_entity_scores")
    op.drop_index("credo_entity_scores_entity_idx", table_name="credo_entity_scores")
    op.drop_table("credo_entity_scores")
    op.drop_table("credo_axes")
    op.drop_table("axes")
