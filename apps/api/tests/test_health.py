import asyncio

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app
from app.modules.health.router import Check, get_health_checks


async def ok() -> None:
    return None


async def broken() -> None:
    raise ConnectionError("down")


async def hangs() -> None:
    await asyncio.sleep(10)


def use_checks(app: FastAPI, checks: dict[str, Check]) -> None:
    app.dependency_overrides[get_health_checks] = lambda: checks


async def test_healthy_when_all_checks_pass(app: FastAPI, client: AsyncClient) -> None:
    use_checks(app, {"database": ok, "redis": ok})

    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


async def test_degraded_when_a_check_fails(app: FastAPI, client: AsyncClient) -> None:
    use_checks(app, {"database": ok, "redis": broken})

    response = await client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "checks": {"database": "ok", "redis": "unavailable"},
    }


async def test_slow_check_times_out(app: FastAPI, client: AsyncClient) -> None:
    use_checks(app, {"database": hangs})

    response = await client.get("/api/health")

    assert response.status_code == 503
    assert response.json()["checks"] == {"database": "unavailable"}


async def test_response_carries_request_id(app: FastAPI, client: AsyncClient) -> None:
    use_checks(app, {"database": ok})

    response = await client.get("/api/health", headers={"X-Request-ID": "abc123"})

    assert response.headers["X-Request-ID"] == "abc123"


@pytest.mark.integration
async def test_health_against_real_services() -> None:
    """Needs Postgres and Redis running (docker compose, or CI services)."""
    app = create_app(Settings(app_env="test"))
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/health")

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ok"
