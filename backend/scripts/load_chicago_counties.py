"""
Load Chicago-area county boundaries into the geographies table.

Downloads the Census TIGER/Line county shapefile, extracts the 7
Chicago-metro counties, and upserts their boundaries.

Usage:
    cd backend
    python scripts/load_chicago_counties.py
"""

import asyncio
import io
import json
import os
import sys
import zipfile

import httpx
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

TIGER_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip"

COUNTIES = {
    "17031": "Cook County, IL",
    "17043": "DuPage County, IL",
    "17097": "Lake County, IL",
    "17197": "Will County, IL",
    "17089": "Kane County, IL",
    "17111": "McHenry County, IL",
    "17093": "Kendall County, IL",
}


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
        shp_data = dbf_data = shx_data = None
        for name in zf.namelist():
            if name.endswith(".shp"):
                shp_data = io.BytesIO(zf.read(name))
            elif name.endswith(".dbf"):
                dbf_data = io.BytesIO(zf.read(name))
            elif name.endswith(".shx"):
                shx_data = io.BytesIO(zf.read(name))

    sf = shapefile.Reader(shp=shp_data, dbf=dbf_data, shx=shx_data)
    fields = [f[0] for f in sf.fields[1:]]

    found: dict[str, tuple] = {}
    for record, shape in zip(sf.records(), sf.shapes()):
        row = dict(zip(fields, record))
        geoid = row.get("GEOID")
        if geoid in COUNTIES:
            found[geoid] = (row, shape)
        if len(found) == len(COUNTIES):
            break

    missing = set(COUNTIES) - set(found)
    if missing:
        print(f"WARNING: Could not find FIPS in shapefile: {missing}")

    async with session_maker() as session:
        for fips, (row, shape) in found.items():
            geojson_geom = shape.__geo_interface__
            if geojson_geom["type"] == "Polygon":
                geojson_geom = {
                    "type": "MultiPolygon",
                    "coordinates": [geojson_geom["coordinates"]],
                }
            geojson_str = json.dumps(geojson_geom)

            await session.execute(
                text("""
                    INSERT INTO geographies (id, name, state_fips, geo_type, boundary)
                    VALUES (
                        :fips, :name, '17', 'county',
                        ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        boundary = EXCLUDED.boundary,
                        name = EXCLUDED.name
                """),
                {"fips": fips, "name": COUNTIES[fips], "geojson": geojson_str},
            )
            print(f"  Loaded {COUNTIES[fips]} ({fips})")

        await session.commit()

    print(f"Done. {len(found)} counties loaded.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(load())
