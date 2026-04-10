from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.agenda import Agenda, AgendaMeans
from models.credo import Credo, CredoEntity, Entity, EntityEvent
from schemas.agenda import AgendaMeansOut, AgendaOut
from schemas.credo import CredoOut
from schemas.entity import CredoEntityOut, EntityEventOut

router = APIRouter(prefix="/api/v1/credos", tags=["credos"])


@router.get("/{username}", response_model=CredoOut)
async def get_credo(username: str, db: AsyncSession = Depends(get_db)) -> CredoOut:
    credo = await db.scalar(select(Credo).where(Credo.username == username))
    if not credo:
        raise HTTPException(status_code=404, detail="Credo not found")

    # Agendas belonging to this credo
    agendas_result = await db.scalars(
        select(Agenda)
        .where(Agenda.credo_id == credo.id, Agenda.status == "active")
        .options(selectinload(Agenda.geographies))
    )
    agendas = agendas_result.all()

    # Means for each agenda — batch load to avoid N+1
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

    # Entities linked to this credo via junction, ordered by score
    rows = (
        await db.execute(
            select(CredoEntity, Entity)
            .join(Entity, CredoEntity.entity_id == Entity.id)
            .where(CredoEntity.credo_id == credo.id)
            .order_by(CredoEntity.impact_score.desc())
        )
    ).all()

    if rows:
        entity_ids = [row.Entity.id for row in rows]
        events_result = await db.scalars(
            select(EntityEvent)
            .where(EntityEvent.entity_id.in_(entity_ids), EntityEvent.reviewed == True)  # noqa: E712
            .order_by(EntityEvent.event_date.desc())
        )
        events_by_entity: dict = defaultdict(list)
        for ev in events_result.all():
            events_by_entity[ev.entity_id].append(
                EntityEventOut(
                    id=ev.id,
                    title=ev.title,
                    description=ev.description,
                    event_date=ev.event_date,
                    metric_id=ev.metric_id,
                    event_impact_score=ev.event_impact_score,
                    source_url=ev.source_url,
                    source_type=ev.source_type,
                )
            )
    else:
        events_by_entity = defaultdict(list)

    return CredoOut(
        id=credo.id,
        username=credo.username,
        title=credo.title,
        description=credo.description,
        agendas=[
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
        ],
        entities=[
            CredoEntityOut(
                id=row.Entity.id,
                name=row.Entity.name,
                type=row.Entity.type,
                description=row.Entity.description,
                impact_score=row.CredoEntity.impact_score,
                events=events_by_entity[row.Entity.id],
            )
            for row in rows
        ],
    )
