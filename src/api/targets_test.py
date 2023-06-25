from datetime import datetime, timedelta
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


async def test_targets_post(created_target: Target) -> None:
    # NOTE: all checks are located inside the created_target fixture
    pass


async def test_targets_post_no_body(client: AsyncClient) -> None:
    response = await client.post("/targets")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_targets_post_get(
    check_empty_targets: None, created_target: Target, client: AsyncClient
) -> None:
    response = await client.get("/targets")
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 1

    got = Target(**json[0])

    assert got == created_target

    response = await client.get(f"/targets/{got.id}")
    assert response.status_code == HTTPStatus.OK
    assert got == Target(**response.json())


async def test_targets_patch(
    created_target: Target, client: AsyncClient
) -> None:
    created_target.description = "new description"
    created_target.current = created_target.target
    body = PatchTarget(**created_target.dict())

    response = await client.patch(
        f"/targets/{created_target.id}", json=body.dict()
    )
    assert response.status_code == HTTPStatus.OK

    got = Target(**response.json())

    created_target.completed = True

    assert got == created_target

    response = await client.get(f"/targets/{got.id}")
    assert response.status_code == HTTPStatus.OK
    assert got == Target(**response.json())


async def test_targets_delete(
    created_target: Target, client: AsyncClient
) -> None:
    response = await client.delete(f"/targets/{created_target.id}")
    assert response.status_code == HTTPStatus.OK

    got = Target(**response.json())

    assert got == created_target

    await assert_returns_empty(client, "/targets")


async def assert_invalid(body: dict[str, Any], client: AsyncClient) -> None:
    response_post = await client.post("/targets", json=body)
    assert response_post.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response_patch = await client.patch("/targets/1", json=body)
    assert response_patch.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_targets_invalid_body(
    created_target: Target, client: AsyncClient
) -> None:
    body = CreateTarget(**created_target.dict())
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
    created_target: Target, client: AsyncClient
) -> None:
    body = PatchTarget(**created_target.dict())
    body.limit = (datetime.now() - timedelta(minutes=5)).isoformat()

    response = await client.patch("/targets/1", json=body.dict())
    assert response.json()["expired"]

    # mypy needs reassurance
    assert body.current is not None
    assert body.target is not None

    body_curr = {**body.dict(), "current": body.current + 1}
    resp_patch = await client.patch("/targets/1", json=body_curr)
    assert resp_patch.status_code == HTTPStatus.CONFLICT

    body_target = {**body.dict(), "target": body.target + 1}
    resp_patch = await client.patch("/targets/1", json=body_target)
    assert resp_patch.status_code == HTTPStatus.CONFLICT
