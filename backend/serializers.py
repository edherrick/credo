"""Shared ORM→schema assembly used by more than one route.

Keeps multi-step response construction (and its N+1-safe batch loading) in one
place so routes don't duplicate it.
"""
from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.agenda import Agenda, AgendaMeans, Means
from schemas.agenda import AgendaMeansOut, AgendaOut


async def build_agenda_outs(db: AsyncSession, agendas: Sequence[Agenda]) -> list[AgendaOut]:
    """Assemble ``AgendaOut`` objects for the given agendas, batch-loading their
    means to avoid an N+1. Shared by the ``/agendas`` and ``/credos`` routes.

    Each agenda must already have its ``geographies`` relationship loaded.
    """
    agenda_ids = [a.id for a in agendas]
    means_by_agenda: dict = defaultdict(list)
    if agenda_ids:
        junction_rows = await db.scalars(
            select(AgendaMeans)
            .where(AgendaMeans.agenda_id.in_(agenda_ids))
            .options(
                selectinload(AgendaMeans.means).selectinload(Means.category),
                selectinload(AgendaMeans.means).selectinload(Means.evidence),
            )
        )
        for jrow in junction_rows.all():
            means_by_agenda[jrow.agenda_id].append(AgendaMeansOut.model_validate(jrow))

    return [
        AgendaOut(
            id=a.id,
            title=a.title,
            metric_id=a.metric_id,
            credo_id=a.credo_id,
            geography_ids=[g.geography_id for g in a.geographies],
            direction=a.direction,
            target_value=float(a.target_value) if a.target_value is not None else None,
            target_date=a.target_date,
            status=a.status,
            means=means_by_agenda[a.id],
        )
        for a in agendas
    ]
