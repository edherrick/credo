import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.credo import Belief

router = APIRouter(prefix="/api/v1/beliefs", tags=["beliefs"])


class BeliefListOut(BaseModel):
    id: uuid.UUID
    title: str
    statement: str
    category: str
    source: str | None
    canonical: bool


@router.get("/", response_model=list[BeliefListOut])
async def list_beliefs(db: AsyncSession = Depends(get_db)) -> list[BeliefListOut]:
    result = await db.scalars(select(Belief).order_by(Belief.category, Belief.title))
    return [
        BeliefListOut(
            id=b.id,
            title=b.title,
            statement=b.statement,
            category=b.category,
            source=b.source,
            canonical=b.canonical,
        )
        for b in result.all()
    ]
