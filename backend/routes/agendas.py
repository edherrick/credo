from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.agenda import Agenda, AgendaMeans
from schemas.agenda import AgendaMeansOut, AgendaOut

router = APIRouter(prefix="/api/v1/agendas", tags=["agendas"])


@router.get("", response_model=list[AgendaOut])
async def list_agendas(db: AsyncSession = Depends(get_db)) -> list[AgendaOut]:
    agendas_result = await db.scalars(
        select(Agenda)
        .where(Agenda.status == "active")
        .options(selectinload(Agenda.geographies))
    )
    agendas = agendas_result.all()

    agenda_ids = [a.id for a in agendas]
    means_by_agenda: dict = defaultdict(list)
    if agenda_ids:
        means_result = await db.scalars(
            select(AgendaMeans).where(AgendaMeans.agenda_id.in_(agenda_ids))
        )
        for m in means_result.all():
            means_by_agenda[m.agenda_id].append(
                AgendaMeansOut(
                    id=m.id,
                    category=m.category,
                    title=m.title,
                    description=m.description,
                    target=m.target,
                )
            )

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
