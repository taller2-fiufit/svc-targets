import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
from http import HTTPStatus
from src.api.model.report import CreateReport, Report
from src.common import TargetType

from src.test_utils import assert_returns_empty
from src.auth import get_admin, get_user, ignore_auth
from src.db.migration import downgrade_db
from src.main import app, lifespan
from src.api.model.target import (
    CreateTarget,
    Multimedia,
    Target,
)


# https://stackoverflow.com/questions/71925980/cannot-perform-operation-another-operation-is-in-progress-in-pytest
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ---------------
# COMMON FIXTURES
# ---------------


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # reset database
    await downgrade_db()

    # https://fastapi.tiangolo.com/advanced/testing-dependencies/
    app.dependency_overrides[get_user] = ignore_auth
    app.dependency_overrides[get_admin] = ignore_auth

    async with lifespan(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client


# -----------------
# TARGET FIXTURES
# -----------------


@pytest.fixture
async def check_empty_targets(client: AsyncClient) -> None:
    await assert_returns_empty(client, "/targets")


@pytest.fixture
async def created_target(client: AsyncClient) -> Target:
    body = CreateTarget(
        name="name",
        description="description",
        type=TargetType.DISTANCE_TRAVELLED,
        limit=(datetime.now(tz=timezone.utc) + timedelta(days=1)).isoformat(),
        current=0.0,
        target=1.0,
        multimedia=[Multimedia("url1"), Multimedia("url2")],
    )

    response = await client.post("/targets", json=body.dict())

    assert response.status_code == HTTPStatus.CREATED

    json = response.json()

    result = CreateTarget(**json)

    assert result == body
    assert not json["completed"]
    assert not json["expired"]

    return Target(**json)


# -----------------
# REPORT FIXTURES
# -----------------


@pytest.fixture
async def check_empty_reports(client: AsyncClient) -> None:
    await assert_returns_empty(client, "/reports")


@pytest.fixture
async def created_report(client: AsyncClient) -> Report:
    # backend uses UTC and without milliseconds
    start = datetime.now(timezone.utc).replace(microsecond=0)

    body = CreateReport(
        type=TargetType.DISTANCE_TRAVELLED,
        count=1.0,
    )

    response = await client.post("/reports", json=body.dict())

    assert response.status_code == HTTPStatus.CREATED

    json = response.json()

    result = CreateReport(**json)

    assert result == body

    report = Report(**json)

    got_date = datetime.fromisoformat(report.date)
    now = datetime.now(timezone.utc)

    assert start <= got_date <= now

    return report
