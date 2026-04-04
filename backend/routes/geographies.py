from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.geography import Geography
from schemas.geography import GeographyOut

router = APIRouter(prefix="/api/v1/geographies", tags=["geographies"])


@router.get("", response_model=list[GeographyOut])
async def list_geographies(db: AsyncSession = Depends(get_db)) -> list[Geography]:
    result = await db.execute(select(Geography))
    return list(result.scalars().all())


@router.get("/{fips}", response_model=GeographyOut)
async def get_geography(fips: str, db: AsyncSession = Depends(get_db)) -> Geography:
    geo = await db.get(Geography, fips)
    if not geo:
        raise HTTPException(status_code=404, detail=f"Geography '{fips}' not found")
    return geo
