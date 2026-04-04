"""
Load Cook County, IL (FIPS 17031) boundary into the geographies table.

Downloads the Census TIGER/Line county shapefile, extracts Cook County,
and upserts it into the database.

Usage:
    cd backend
    python scripts/load_cook_county.py
"""

import asyncio
import io
import os
import sys
import zipfile

import httpx
from dotenv import load_dotenv
import json

# Add backend root to path so imports work when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

TIGER_URL = (
    "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"
)
COOK_COUNTY_FIPS = "17031"
STATE_FIPS = "17"


async def load() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy import text

    database_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(database_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    print("Downloading Census TIGER/Line county shapefile…")
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(TIGER_URL)
        response.raise_for_status()

    print("Extracting shapefile…")
    import shapefile  # pyshp

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        # Extract all files to a temp buffer
        shp_data = dbf_data = shx_data = None
        for name in zf.namelist():
            if name.endswith(".shp"):
                shp_data = io.BytesIO(zf.read(name))
            elif name.endswith(".dbf"):
                dbf_data = io.BytesIO(zf.read(name))
            elif name.endswith(".shx"):
                shx_data = io.BytesIO(zf.read(name))

    sf = shapefile.Reader(shp=shp_data, dbf=dbf_data, shx=shx_data)
    fields = [f[0] for f in sf.fields[1:]]  # skip DeletionFlag

    cook = None
    for record, shape in zip(sf.records(), sf.shapes()):
        row = dict(zip(fields, record))
        if row.get("GEOID") == COOK_COUNTY_FIPS:
            cook = (row, shape)
            break

    if not cook:
        print(f"ERROR: Could not find FIPS {COOK_COUNTY_FIPS} in shapefile")
        sys.exit(1)

    row, shape = cook
    # pyshp Shape supports __geo_interface__ for GeoJSON-compatible dict
    geojson_geom = shape.__geo_interface__
    # Ensure it's a MultiPolygon (Census TIGER counties are always Polygon or MultiPolygon)
    if geojson_geom["type"] == "Polygon":
        geojson_geom = {"type": "MultiPolygon", "coordinates": [geojson_geom["coordinates"]]}

    geojson_str = json.dumps(geojson_geom)

    print(f"Inserting Cook County boundary (type: {geojson_geom['type']})…")
    async with session_maker() as session:
        await session.execute(
            text("""
                INSERT INTO geographies (id, name, state_fips, geo_type, boundary)
                VALUES (
                    :fips,
                    :name,
                    :state_fips,
                    'county',
                    ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                )
                ON CONFLICT (id) DO UPDATE SET
                    boundary = EXCLUDED.boundary,
                    name = EXCLUDED.name
            """),
            {
                "fips": COOK_COUNTY_FIPS,
                "name": "Cook County, IL",
                "state_fips": STATE_FIPS,
                "geojson": geojson_str,
            },
        )
        await session.commit()

    print("Done. Cook County loaded successfully.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(load())
