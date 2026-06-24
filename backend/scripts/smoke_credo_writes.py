"""Manual smoke test for the credo write/ownership pattern.

Runs the real FastAPI app in-process (httpx ASGITransport) against the live dev
Postgres, exercises the full create/auth/ownership/update/delete flow, then
cleans up the users it created. This is a smoke tool, not the eventual pytest
harness (which should use an isolated/transactional test DB).

Run from the backend/ directory with the venv:
    .venv/bin/python scripts/smoke_credo_writes.py
"""
import asyncio
import os
import sys
import uuid

# Make backend/ importable regardless of how this script is invoked.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
import psycopg2
from httpx import ASGITransport

import main

PW = "testpass123"


async def run() -> list[str]:
    emails: list[str] = []
    transport = ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        async def make_user(tag: str) -> dict:
            email = f"smoke_{tag}_{uuid.uuid4().hex[:8]}@example.com"
            emails.append(email)
            r = await c.post(
                "/api/v1/auth/register",
                json={"email": email, "password": PW, "username": "u" + uuid.uuid4().hex[:8]},
            )
            assert r.status_code in (200, 201), ("register", r.status_code, r.text)
            r = await c.post("/api/v1/auth/login", data={"username": email, "password": PW})
            assert r.status_code == 200, ("login", r.status_code, r.text)
            return {"Authorization": f"Bearer {r.json()['access_token']}"}

        owner = await make_user("owner")
        other = await make_user("other")
        handle = "smoke-" + uuid.uuid4().hex[:6]

        # anonymous create -> 401
        r = await c.post("/api/v1/credos", json={"username": handle, "title": "T"})
        assert r.status_code == 401, ("anon create should 401", r.status_code)

        # reserved handle -> 422
        r = await c.post("/api/v1/credos", json={"username": "new", "title": "T"}, headers=owner)
        assert r.status_code == 422, ("reserved handle should 422", r.status_code, r.text)

        # create (owner)
        r = await c.post(
            "/api/v1/credos",
            json={"username": handle, "title": "Smoke Test", "description": "x"},
            headers=owner,
        )
        assert r.status_code == 201, ("create", r.status_code, r.text)
        created = r.json()
        assert created["username"] == handle and created["owner_id"], created

        # duplicate handle -> 409
        r = await c.post("/api/v1/credos", json={"username": handle, "title": "T2"}, headers=owner)
        assert r.status_code == 409, ("dup handle should 409", r.status_code)

        # GET exposes owner_id
        r = await c.get(f"/api/v1/credos/{handle}")
        assert r.status_code == 200 and r.json()["owner_id"] == created["owner_id"], r.text

        # non-owner PATCH / DELETE -> 403  (the core authz guarantee)
        r = await c.patch(f"/api/v1/credos/{handle}", json={"title": "Hijack"}, headers=other)
        assert r.status_code == 403, ("non-owner patch should 403", r.status_code, r.text)
        r = await c.delete(f"/api/v1/credos/{handle}", headers=other)
        assert r.status_code == 403, ("non-owner delete should 403", r.status_code)

        # owner PATCH -> 200, partial update
        r = await c.patch(f"/api/v1/credos/{handle}", json={"title": "Renamed"}, headers=owner)
        assert r.status_code == 200 and r.json()["title"] == "Renamed", ("owner patch", r.status_code, r.text)

        # owner DELETE -> 204, then gone
        r = await c.delete(f"/api/v1/credos/{handle}", headers=owner)
        assert r.status_code == 204, ("owner delete", r.status_code, r.text)
        r = await c.get(f"/api/v1/credos/{handle}")
        assert r.status_code == 404, ("should be gone", r.status_code)

    return emails


def main_() -> None:
    emails = asyncio.run(run())
    conn = psycopg2.connect(host="localhost", port=5433, user="credo", password="credo", dbname="credo")
    cur = conn.cursor()
    for email in emails:
        cur.execute("delete from user_profiles where user_id in (select id from users where email=%s)", (email,))
        cur.execute("delete from users where email=%s", (email,))
    conn.commit()
    print("SMOKE OK — 401/422/201/409/403/200/204/404 all verified; test users cleaned up")


if __name__ == "__main__":
    main_()
