from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.credo import Entity, EntityEvent
from schemas.entity import EntityDetailOut, EntityEventOut

router = APIRouter(prefix="/api/v1/entities", tags=["entities"])


@router.get("", response_model=list[EntityDetailOut])
async def list_entities(db: AsyncSession = Depends(get_db)) -> list[EntityDetailOut]:
    result = await db.scalars(select(Entity).order_by(Entity.name))
    return [
        EntityDetailOut(
            id=e.id,
            name=e.name,
            slug=e.slug,
            type=e.type,
            description=e.description,
            wikidata_id=e.wikidata_id,
            events=[],
        )
        for e in result.all()
    ]


@router.get("/{slug}", response_model=EntityDetailOut)
async def get_entity(slug: str, db: AsyncSession = Depends(get_db)) -> EntityDetailOut:
    entity = await db.scalar(select(Entity).where(Entity.slug == slug))
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    events_result = await db.scalars(
        select(EntityEvent)
        .where(EntityEvent.entity_id == entity.id, EntityEvent.reviewed == True)  # noqa: E712
        .order_by(EntityEvent.event_date.desc().nullslast(), EntityEvent.title)
    )

    events = [
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
        for ev in events_result.all()
    ]

    return EntityDetailOut(
        id=entity.id,
        name=entity.name,
        slug=entity.slug,
        type=entity.type,
        description=entity.description,
        wikidata_id=entity.wikidata_id,
        events=events,
    )
