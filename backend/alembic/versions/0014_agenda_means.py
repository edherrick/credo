"""Add agenda_means table — policy instruments for achieving an agenda's goal

Taxonomy: incentive, penalty, mandate, boycott, divestment, zoning,
          litigation, petition, subsidy

Revision ID: 0014
Revises: 0013
Create Date: 2026-04-09
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CATEGORIES = (
    "incentive", "penalty", "mandate", "boycott", "divestment",
    "zoning", "litigation", "petition", "subsidy",
)


def upgrade() -> None:
    op.create_table(
        "agenda_means",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
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
        sa.CheckConstraint(
            f"category IN {CATEGORIES}",
            name="agenda_means_category_check",
        ),
    )

    # Seed means for the existing Chicago metro housing agenda
    op.execute("""
        INSERT INTO agenda_means (agenda_id, category, title, description, target)
        SELECT
            a.id,
            m.category,
            m.title,
            m.description,
            m.target
        FROM agendas a
        CROSS JOIN (VALUES
            (
                'incentive',
                'First-time buyer down payment grants',
                'State-funded grants of up to $15,000 for first-time buyers earning at or below '
                '80% of area median income. Disbursed at closing; no repayment required if the '
                'buyer occupies the property for five or more years.',
                'First-time homebuyers earning ≤80% AMI'
            ),
            (
                'penalty',
                'Vacancy tax on investor-held residential properties',
                'Annual tax on residential properties held vacant for more than six months '
                'by entities that own three or more units. Rate: 1% of assessed value per year, '
                'rising to 3% after two consecutive vacant years.',
                'Institutional and speculative property owners'
            ),
            (
                'mandate',
                '20% affordable inclusionary zoning requirement',
                'Require that 20% of units in any new residential development of 10 or more '
                'units be offered at affordable rates (≤80% AMI for ownership, ≤60% AMI for '
                'rental). Developers may pay an in-lieu fee at $50k per required unit.',
                'All residential developers in covered municipalities'
            ),
            (
                'boycott',
                'Institutional divestment from single-family rental REITs',
                'Campaign targeting pension funds, university endowments, and sovereign wealth '
                'funds to divest equity holdings in single-family rental real estate investment '
                'trusts operating in the Chicago metro area.',
                'Pension funds, endowments, and institutional investors'
            ),
            (
                'zoning',
                'Transit-corridor upzoning to increase housing supply',
                'Rezone parcels within a half-mile of CTA and Metra stations to permit '
                'mid-rise residential (4–8 stories) by right. Removes the current variance '
                'requirement that adds 18–36 months to project timelines.',
                'Municipalities with transit station areas currently zoned single-family'
            ),
            (
                'subsidy',
                'Community land trust capitalisation fund',
                'Allocate $50M in state capital to expand the Chicago Community Land Trust '
                'model to all seven Chicago-area counties, enabling permanent affordability '
                'preservation for at least 500 additional units over five years.',
                'Chicago Community Land Trust and affiliated municipal land trusts'
            )
        ) AS m(category, title, description, target)
        WHERE a.metric_id = 'median_home_price'
    """)


def downgrade() -> None:
    op.drop_table("agenda_means")
