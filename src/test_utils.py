from typing import Any
from httpx import AsyncClient
from http import HTTPStatus

from src.common import TargetType


async def assert_returns_empty(client: AsyncClient, url: str) -> None:
    response = await client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


async def assert_empty_reports(
    client: AsyncClient, params: dict[str, Any] = {}
) -> None:
    response = await client.get("/reports", params=params)

    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == len(TargetType)
    for rep in json:
        assert rep["count"] == 0.0
