"""Restructure agenda_means into a reusable policy means repository

Adds:
  - means_categories: taxonomy of policy instrument types (TEXT PK, like metrics)
  - means: the canonical library of policy instruments
  - means_evidence: historical evidence of a means working in a specific context

Restructures:
  - agenda_means: was a child of agendas (one row per instrument per agenda);
    becomes a junction table (agenda_id, means_id) so instruments are reusable
    across agendas and evidence accumulates on the instrument itself.

Migration path for existing seed data:
  1. Insert means_categories from the 9 existing CHECK-constraint values
  2. Insert one means row per distinct (category, title) in the old agenda_means
  3. Create new agenda_means_new junction table and migrate rows
  4. Swap old table out, rename new table in

Revision ID: 0017
Revises: 0016
Create Date: 2026-04-12
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Seed data: map old category values → (label, family, description)
CATEGORY_SEED = [
    (
        "incentive",
        "Incentive",
        "fiscal",
        "Financial rewards or benefits that encourage a desired behaviour (grants, tax credits, rebates).",
    ),
    (
        "penalty",
        "Penalty",
        "fiscal",
        "Financial disincentives applied to undesired behaviour (vacancy taxes, fines, surcharges).",
    ),
    (
        "subsidy",
        "Subsidy",
        "fiscal",
        "Direct public funding to reduce the cost of a good or service (capital grants, operating subsidies).",
    ),
    (
        "mandate",
        "Mandate",
        "regulatory",
        "Legal requirements imposed on private actors (inclusionary zoning, building codes, set-asides).",
    ),
    (
        "zoning",
        "Zoning Reform",
        "regulatory",
        "Changes to land-use rules that expand or restrict what can be built where (upzoning, by-right approval).",
    ),
    (
        "litigation",
        "Litigation",
        "civic",
        "Legal action to enforce existing rights or challenge unlawful practices.",
    ),
    (
        "petition",
        "Petition / Advocacy",
        "civic",
        "Organised public pressure on decision-makers through petitions, public comment, or campaigns.",
    ),
    (
        "boycott",
        "Boycott",
        "market",
        "Coordinated refusal to engage with specific actors — purchasing boycotts or investment divestment campaigns.",
    ),
    (
        "divestment",
        "Divestment",
        "market",
        "Withdrawal of capital from industries, funds, or assets that perpetuate the problem.",
    ),
]


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. means_categories                                                  #
    # ------------------------------------------------------------------ #
    op.create_table(
        "means_categories",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("label", sa.Text, nullable=False),
        sa.Column("family", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "family IN ('fiscal', 'regulatory', 'civic', 'market')",
            name="means_categories_family_check",
        ),
    )

    for cat_id, label, family, description in CATEGORY_SEED:
        op.execute(
            sa.text(
                "INSERT INTO means_categories (id, label, family, description) "
                "VALUES (:id, :label, :family, :description)"
            ).bindparams(id=cat_id, label=label, family=family, description=description)
        )

    # ------------------------------------------------------------------ #
    # 2. means (the repository)                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "means",
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "category_id",
            sa.Text,
            sa.ForeignKey("means_categories.id"),
            nullable=False,
        ),
        sa.Column(
            "canonical",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # ------------------------------------------------------------------ #
    # 3. Migrate existing agenda_means rows into means                     #
    #    One means row per distinct (category, title) from old table.      #
    # ------------------------------------------------------------------ #
    op.execute("""
        INSERT INTO means (title, description, category_id, canonical)
        SELECT DISTINCT ON (category, title)
            title,
            description,
            category   AS category_id,
            TRUE       AS canonical
        FROM agenda_means
        ORDER BY category, title, created_at
    """)

    # ------------------------------------------------------------------ #
    # 4. Build the new junction table                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "agenda_means_new",
        sa.Column(
            "agenda_id",
            sa.UUID,
            sa.ForeignKey("agendas.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "means_id",
            sa.UUID,
            sa.ForeignKey("means.id", ondelete="RESTRICT"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Map old rows → junction rows via the means we just inserted
    op.execute("""
        INSERT INTO agenda_means_new (agenda_id, means_id, created_at)
        SELECT
            am.agenda_id,
            m.id,
            am.created_at
        FROM agenda_means am
        JOIN means m
          ON m.category_id = am.category
         AND m.title       = am.title
    """)

    # ------------------------------------------------------------------ #
    # 5. Swap tables                                                        #
    # ------------------------------------------------------------------ #
    op.drop_table("agenda_means")
    op.rename_table("agenda_means_new", "agenda_means")

    # ------------------------------------------------------------------ #
    # 6. means_evidence                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "means_evidence",
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "means_id",
            sa.UUID,
            sa.ForeignKey("means.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column(
            "geography_id",
            sa.Text,
            sa.ForeignKey("geographies.id"),
            nullable=True,
        ),
        sa.Column("outcome", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "outcome IN ('reduced', 'increased', 'mixed', 'inconclusive')",
            name="means_evidence_outcome_check",
        ),
    )


def downgrade() -> None:
    op.drop_table("means_evidence")

    # Restore agenda_means as the original child table
    op.create_table(
        "agenda_means_old",
        sa.Column(
            "id",
            sa.UUID,
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "agenda_id",
            sa.UUID,
            sa.ForeignKey("agendas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("target", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.execute("""
        INSERT INTO agenda_means_old (agenda_id, category, title, description, created_at)
        SELECT
            am.agenda_id,
            m.category_id,
            m.title,
            m.description,
            am.created_at
        FROM agenda_means am
        JOIN means m ON m.id = am.means_id
    """)

    op.drop_table("agenda_means")
    op.rename_table("agenda_means_old", "agenda_means")

    op.drop_table("means")
    op.drop_table("means_categories")
