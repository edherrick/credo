"""Shared pytest fixtures.

Scaffold only — kept intentionally light while the project is in active
development. The `client` fixture drives the app in-process via ASGI (no running
server, no network), so route smoke tests are cheap. Tests that need the
database can request a session fixture once one is added here.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client() -> AsyncClient:
    """An httpx client wired straight to the FastAPI app (in-process ASGI)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
