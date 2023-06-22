from datetime import datetime
from typing import Any
from httpx import AsyncClient
from http import HTTPStatus

from src.api.model.target import (
    CreateTarget,
    PatchTarget,
    Target,
)
from src.test_utils import assert_returns_empty


async def test_targets_get_empty(check_empty_targets: None) -> None:
    # NOTE: all checks are located inside the check_empty_targets fixture
    pass


async def test_targets_get_nonexistent(client: AsyncClient) -> None:
    response = await client.get("/targets/1")

    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_targets_post(created_body: Target) -> None:
    # NOTE: all checks are located inside the created_body fixture
    pass


async def test_targets_post_no_body(client: AsyncClient) -> None:
    response = await client.post("/targets")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_targets_post_get(
    check_empty_targets: None, created_body: Target, client: AsyncClient
) -> None:
    response = await client.get("/targets")
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 1

    got = Target(**json[0])

    assert got == created_body

    response = await client.get(f"/targets/{got.id}")
    assert response.status_code == HTTPStatus.OK
    assert got == Target(**response.json())


async def test_targets_patch(
    created_body: Target, client: AsyncClient
) -> None:
    created_body.description = "new description"
    created_body.current = created_body.target
    body = PatchTarget(**created_body.dict())

    response = await client.patch(
        f"/targets/{created_body.id}", json=body.dict()
    )
    assert response.status_code == HTTPStatus.OK

    got = Target(**response.json())

    created_body.completed = True

    assert got == created_body

    response = await client.get(f"/targets/{got.id}")
    assert response.status_code == HTTPStatus.OK
    assert got == Target(**response.json())


async def test_targets_delete(
    created_body: Target, client: AsyncClient
) -> None:
    response = await client.delete(f"/targets/{created_body.id}")
    assert response.status_code == HTTPStatus.OK

    got = Target(**response.json())

    assert got == created_body

    await assert_returns_empty(client, "/targets")


async def assert_invalid(body: dict[str, Any], client: AsyncClient) -> None:
    response_post = await client.post("/targets", json=body)
    assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response_patch = await client.patch("/targets/1", json=body)
    assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_targets_invalid_body(
    created_body: Target, client: AsyncClient
) -> None:
    body = CreateTarget(**created_body.dict())
    assert body.target is not None
    body.name = "other name"

    # NOTE: we edit the dict because the model types contain validations

    # too long name
    await assert_invalid({**body.dict(), "name": "a" * 31}, client)

    # short name
    await assert_invalid({**body.dict(), "name": ""}, client)

    # too long description
    await assert_invalid({**body.dict(), "description": "a" * 301}, client)

    # too many multimedia resources
    await assert_invalid({**body.dict(), "multimedia": ["url"] * 5}, client)

    # too long multimedia url
    await assert_invalid({**body.dict(), "multimedia": ["a" * 256]}, client)

    # current is greater than target
    # - in POST it fails
    req_body = {**body.dict(), "current": body.target + 1}
    resp_post = await client.post("/targets", json=req_body)
    assert resp_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # - in PATCH it saturates to target
    resp_patch = await client.patch("/targets/1", json=req_body)
    assert resp_patch.status_code == HTTPStatus.OK
    assert resp_patch.json()["current"] == body.target


async def test_cannot_modify_expired_target(
        created_body: Target, client: AsyncClient
) -> None:
    body = CreateTarget(**created_body.dict())
    body.limit = (datetime.now().timestamp() - 9) * 1000

    response = await client.patch("/targets/1", json=body.dict())
    assert response.expired

    body.name = "other name"

    await assert_invalid({**body.dict(), "current": body.current + 1}, client)
    await assert_invalid({**body.dict(), "target": body.target + 1}, client)
