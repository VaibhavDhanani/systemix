from fastapi import FastAPI
from httpx import AsyncClient

from app.core.errors import AppError


async def test_unknown_route_uses_error_shape(client: AsyncClient) -> None:
    response = await client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "http_404", "message": "Not Found", "details": None}
    }


async def test_validation_error_shape(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/api/_test/items/{item_id}")
    async def item(item_id: int) -> dict[str, int]:
        return {"id": item_id}

    response = await client.get("/api/_test/items/not-a-number")

    body = response.json()["error"]
    assert response.status_code == 422
    assert body["code"] == "validation_error"
    assert body["details"][0]["loc"] == ["path", "item_id"]


async def test_app_error_shape(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/api/_test/conflict")
    async def conflict() -> None:
        raise AppError("slot_taken", "That slot was just booked", status_code=409)

    response = await client.get("/api/_test/conflict")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "slot_taken"


async def test_unhandled_error_hides_details(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/api/_test/boom")
    async def boom() -> None:
        raise RuntimeError("secret internal detail")

    response = await client.get("/api/_test/boom")

    assert response.status_code == 500
    assert response.json()["error"] == {
        "code": "internal_error",
        "message": "Something went wrong",
        "details": None,
    }
