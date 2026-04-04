from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.agenda import Agenda
from schemas.agenda import AgendaOut

router = APIRouter(prefix="/api/v1/agendas", tags=["agendas"])


@router.get("", response_model=list[AgendaOut])
async def list_agendas(db: AsyncSession = Depends(get_db)) -> list[Agenda]:
    result = await db.execute(select(Agenda).where(Agenda.status == "active"))
    return list(result.scalars().all())
