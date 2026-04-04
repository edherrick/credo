import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.geography import Geography
from models.metric import Metric, MetricValue
from schemas.metric import MetricOut, MetricValuePoint, MetricValuesOut

router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/metrics", response_model=list[MetricOut])
async def list_metrics(db: AsyncSession = Depends(get_db)) -> list[Metric]:
    result = await db.execute(select(Metric))
    return list(result.scalars().all())


@router.get("/metrics/{metric_id}", response_model=MetricOut)
async def get_metric(metric_id: str, db: AsyncSession = Depends(get_db)) -> Metric:
    metric = await db.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")
    return metric


@router.get("/geographies/{fips}/metrics/{metric_id}/values", response_model=MetricValuesOut)
async def get_metric_values(
    fips: str,
    metric_id: str,
    date_from: datetime.date | None = Query(default=None),
    date_to: datetime.date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> MetricValuesOut:
    geo = await db.get(Geography, fips)
    if not geo:
        raise HTTPException(status_code=404, detail=f"Geography '{fips}' not found")
    metric = await db.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")

    q = select(MetricValue).where(
        MetricValue.metric_id == metric_id,
        MetricValue.geography_id == fips,
    )
    if date_from:
        q = q.where(MetricValue.date >= date_from)
    if date_to:
        q = q.where(MetricValue.date <= date_to)
    q = q.order_by(MetricValue.date)

    result = await db.execute(q)
    rows = result.scalars().all()

    return MetricValuesOut(
        metric_id=metric_id,
        geography_id=fips,
        unit=metric.unit,
        values=[MetricValuePoint(date=r.date, value=float(r.value)) for r in rows],
    )


@router.get("/geographies/{fips}/metrics/{metric_id}/geojson")
async def get_metric_geojson(
    fips: str,
    metric_id: str,
    date: datetime.date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    geo = await db.get(Geography, fips)
    if not geo:
        raise HTTPException(status_code=404, detail=f"Geography '{fips}' not found")
    metric = await db.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")

    # Use PostGIS ST_AsGeoJSON — geometry serialisation stays in the database
    if date:
        sql = text("""
            SELECT
                ST_AsGeoJSON(g.boundary)::json AS geometry,
                mv.value,
                mv.date
            FROM geographies g
            JOIN metric_values mv
                ON mv.geography_id = g.id
                AND mv.metric_id = :metric_id
                AND mv.date = :date
            WHERE g.id = :fips
        """)
        row = (await db.execute(sql, {"fips": fips, "metric_id": metric_id, "date": date})).first()
    else:
        sql = text("""
            SELECT
                ST_AsGeoJSON(g.boundary)::json AS geometry,
                mv.value,
                mv.date
            FROM geographies g
            JOIN metric_values mv
                ON mv.geography_id = g.id
                AND mv.metric_id = :metric_id
            WHERE g.id = :fips
            ORDER BY mv.date DESC
            LIMIT 1
        """)
        row = (await db.execute(sql, {"fips": fips, "metric_id": metric_id})).first()

    if not row:
        raise HTTPException(status_code=404, detail="No data found for the requested date")

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": row.geometry,
                "properties": {
                    "geography_id": fips,
                    "geography_name": geo.name,
                    "metric_id": metric_id,
                    "value": float(row.value),
                    "unit": metric.unit,
                    "date": str(row.date),
                },
            }
        ],
    }
