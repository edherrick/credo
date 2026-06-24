from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.credo import Axis

router = APIRouter(prefix="/api/v1/axes", tags=["axes"])


class AxisListOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    label: str
    description: str | None
    family: str
    canonical: bool


@router.get("", response_model=list[AxisListOut])
async def list_axes(db: AsyncSession = Depends(get_db)) -> list[AxisListOut]:
    result = await db.scalars(select(Axis).order_by(Axis.family, Axis.label))
    return [AxisListOut.model_validate(a) for a in result.all()]
