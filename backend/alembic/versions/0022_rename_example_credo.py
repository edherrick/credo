"""Rename the seeded demo credo handle from 'ed' to 'example'.

The Phase-1 seed credo (migration 0012) used the maintainer's handle 'ed'. Give
the public example a neutral handle so the homepage CTAs link to /credo/example
instead of a personal handle. Relationships key on credo_id, so the rename is safe.

Revision ID: 0022
Revises: 0021
Create Date: 2026-06-22
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0022"
down_revision: Union[str, None] = "0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE credos SET username = 'example' WHERE username = 'ed'")


def downgrade() -> None:
    op.execute("UPDATE credos SET username = 'ed' WHERE username = 'example'")
