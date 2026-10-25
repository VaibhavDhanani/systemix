import asyncio
import logging
from collections.abc import Awaitable, Callable
from functools import partial
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

Check = Callable[[], Awaitable[None]]
CheckStatus = Literal["ok", "unavailable"]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    checks: dict[str, CheckStatus]


async def check_database(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


async def check_redis(redis: Redis) -> None:
    await redis.ping()


def get_health_checks(request: Request) -> dict[str, Check]:
    state = request.app.state
    return {
        "database": partial(check_database, state.engine),
        "redis": partial(check_redis, state.redis),
    }


async def _run(name: str, check: Check, limit_seconds: float) -> CheckStatus:
    try:
        async with asyncio.timeout(limit_seconds):
            await check()
    except Exception:
        logger.warning("health check failed: %s", name, exc_info=True)
        return "unavailable"
    return "ok"


@router.get("/health", response_model=HealthResponse)
async def health(
    request: Request,
    response: Response,
    checks: Annotated[dict[str, Check], Depends(get_health_checks)],
) -> HealthResponse:
    limit = request.app.state.settings.health_check_timeout_seconds
    names = list(checks)
    results = await asyncio.gather(*(_run(name, checks[name], limit) for name in names))
    statuses = dict(zip(names, results, strict=True))
    healthy = all(status == "ok" for status in statuses.values())
    if not healthy:
        response.status_code = 503
    return HealthResponse(status="ok" if healthy else "degraded", checks=statuses)
