"""Smoke test — proves the test harness, app wiring, and ASGI client all work.

This is the seed of the backend suite; real route/DB tests can follow the same
pattern (request the `client` fixture, await a call, assert on the response).
"""


async def test_health(client) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
