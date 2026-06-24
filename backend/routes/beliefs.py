from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.credo import Belief
from schemas.belief import BeliefOut

router = APIRouter(prefix="/api/v1/beliefs", tags=["beliefs"])


@router.get("", response_model=list[BeliefOut])
async def list_beliefs(db: AsyncSession = Depends(get_db)) -> list[BeliefOut]:
    result = await db.scalars(select(Belief).order_by(Belief.category, Belief.title))
    return [BeliefOut.model_validate(b) for b in result.all()]
