import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.geography import Geography
from models.metric import Metric, MetricValue
from schemas.metric import CountySeries, MetricAggregateOut, MetricOut, MetricValuePoint, MetricValuesOut

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
        q = q.where(MetricValue.period_start >= date_from)
    if date_to:
        q = q.where(MetricValue.period_start <= date_to)
    q = q.order_by(MetricValue.period_start)

    result = await db.execute(q)
    rows = result.scalars().all()

    return MetricValuesOut(
        metric_id=metric_id,
        geography_id=fips,
        unit=metric.unit,
        values=[MetricValuePoint(period_start=r.period_start, period_end=r.period_end, value=float(r.value)) for r in rows],
    )


@router.get("/metrics/{metric_id}/geojson")
async def get_state_metric_geojson(
    metric_id: str,
    state_fips: str = Query(..., description="State FIPS, e.g. '17' for Illinois"),
    date: datetime.date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return a GeoJSON FeatureCollection of all counties in a state for a given metric."""
    metric = await db.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")

    if date:
        sql = text("""
            SELECT
                g.id,
                g.name,
                ST_AsGeoJSON(g.boundary)::json AS geometry,
                mv.value,
                mv.period_start
            FROM geographies g
            JOIN metric_values mv
                ON mv.geography_id = g.id
                AND mv.metric_id   = :metric_id
                AND mv.period_start        = :date
            WHERE g.state_fips = :state_fips
              AND g.boundary IS NOT NULL
            ORDER BY g.id
        """)
        rows = (await db.execute(sql, {"metric_id": metric_id, "state_fips": state_fips, "date": date})).all()
    else:
        # Latest available date per county
        sql = text("""
            SELECT DISTINCT ON (g.id)
                g.id,
                g.name,
                ST_AsGeoJSON(g.boundary)::json AS geometry,
                mv.value,
                mv.period_start
            FROM geographies g
            JOIN metric_values mv
                ON mv.geography_id = g.id
                AND mv.metric_id   = :metric_id
            WHERE g.state_fips = :state_fips
              AND g.boundary IS NOT NULL
            ORDER BY g.id, mv.period_start DESC
        """)
        rows = (await db.execute(sql, {"metric_id": metric_id, "state_fips": state_fips})).all()

    features = [
        {
            "type": "Feature",
            "geometry": row.geometry,
            "properties": {
                "geography_id": row.id,
                "geography_name": row.name,
                "metric_id": metric_id,
                "value": float(row.value),
                "unit": metric.unit,
                "period_start": str(row.period_start),
            },
        }
        for row in rows
    ]

    return {"type": "FeatureCollection", "features": features}


@router.get("/metrics/{metric_id}/aggregate", response_model=MetricAggregateOut)
async def get_metric_aggregate(
    metric_id: str,
    state_fips: str = Query(..., description="State FIPS, e.g. '17' for Illinois"),
    db: AsyncSession = Depends(get_db),
) -> MetricAggregateOut:
    """Return per-date average + per-county series for all counties in a state."""
    metric = await db.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_id}' not found")

    # Cross-join all dates × all counties so every county has a value (or null) for every
    # date, preventing polyline index misalignment in the frontend chart.
    sql = text("""
        WITH dates AS (
            SELECT DISTINCT mv.period_start
            FROM metric_values mv
            JOIN geographies g ON g.id = mv.geography_id
            WHERE mv.metric_id = :metric_id AND g.state_fips = :state_fips
        ),
        counties AS (
            SELECT g.id, g.name
            FROM geographies g
            WHERE g.state_fips = :state_fips
              AND EXISTS (
                SELECT 1 FROM metric_values mv
                WHERE mv.geography_id = g.id AND mv.metric_id = :metric_id
              )
        )
        SELECT
            d.period_start,
            AVG(mv.value)::float                       AS avg_value,
            JSON_AGG(
                JSON_BUILD_OBJECT(
                    'geography_id', c.id,
                    'name',         c.name,
                    'value',        mv.value::float
                ) ORDER BY c.id
            ) AS counties
        FROM dates d
        CROSS JOIN counties c
        LEFT JOIN metric_values mv
            ON mv.geography_id = c.id
           AND mv.metric_id    = :metric_id
           AND mv.period_start = d.period_start
        GROUP BY d.period_start
        ORDER BY d.period_start
    """)
    rows = (await db.execute(sql, {"metric_id": metric_id, "state_fips": state_fips})).all()

    if not rows:
        return MetricAggregateOut(metric_id=metric_id, dates=[], avg_values=[], counties=[])

    dates = [str(row.period_start) for row in rows]
    avg_values = [row.avg_value for row in rows]

    # county_map preserves insertion order (Python 3.7+); each county gets one value per
    # date in lockstep with the dates list — null where no data exists.
    county_map: dict[str, dict] = {}
    for row in rows:
        for entry in row.counties:
            gid = entry["geography_id"]
            if gid not in county_map:
                county_map[gid] = {"id": gid, "name": entry["name"], "values": []}
            county_map[gid]["values"].append(entry["value"])  # may be None for sparse dates

    counties = [CountySeries(**c) for c in county_map.values()]
    return MetricAggregateOut(metric_id=metric_id, dates=dates, avg_values=avg_values, counties=counties)


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
                mv.period_start
            FROM geographies g
            JOIN metric_values mv
                ON mv.geography_id = g.id
                AND mv.metric_id = :metric_id
                AND mv.period_start = :date
            WHERE g.id = :fips
        """)
        row = (await db.execute(sql, {"fips": fips, "metric_id": metric_id, "date": date})).first()
    else:
        sql = text("""
            SELECT
                ST_AsGeoJSON(g.boundary)::json AS geometry,
                mv.value,
                mv.period_start
            FROM geographies g
            JOIN metric_values mv
                ON mv.geography_id = g.id
                AND mv.metric_id = :metric_id
            WHERE g.id = :fips
            ORDER BY mv.period_start DESC
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
                    "period_start": str(row.period_start),
                },
            }
        ],
    }
