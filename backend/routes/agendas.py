from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.agenda import Agenda
from schemas.agenda import AgendaOut
from serializers import build_agenda_outs

router = APIRouter(prefix="/api/v1/agendas", tags=["agendas"])


@router.get("", response_model=list[AgendaOut])
async def list_agendas(db: AsyncSession = Depends(get_db)) -> list[AgendaOut]:
    agendas = (
        await db.scalars(
            select(Agenda)
            .where(Agenda.status == "active")
            .options(selectinload(Agenda.geographies))
        )
    ).all()
    return await build_agenda_outs(db, agendas)
