from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from http import HTTPStatus

from src.api.model.report import Report
from src.api.model.target import Target
from src.test_utils import assert_empty_reports


async def test_reports_get_empty(check_empty_reports: None) -> None:
    # NOTE: all checks are located inside the check_empty_reports fixture
    pass


async def test_reports_post(created_report: Report) -> None:
    # NOTE: all checks are located inside the created_report fixture
    pass


async def test_reports_post_no_body(client: AsyncClient) -> None:
    response = await client.post("/reports")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_reports_post_get(
    check_empty_reports: None, created_report: Report, client: AsyncClient
) -> None:
    response = await client.get("/reports")
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 4

    assert created_report in [Report(**rep) for rep in json]


async def test_reports_date_filters(
    check_empty_reports: None, created_report: Report, client: AsyncClient
) -> None:
    # [start, end] doesn't include created_report.date
    start = datetime.now(timezone.utc) - timedelta(minutes=10)
    end = datetime.now(timezone.utc) - timedelta(minutes=5)
    params = {"start": start.isoformat(), "end": end.isoformat()}

    await assert_empty_reports(client, params=params)

    # [start, end] does include created_report.date
    params["end"] = datetime.now(timezone.utc).isoformat()

    response = await client.get("/reports", params=params)
    assert response.status_code == HTTPStatus.OK
    json = response.json()

    assert len(json) == 4
    assert created_report in [Report(**rep) for rep in json]


async def test_report_and_target_post_get(
    check_empty_reports: None,
    created_target: Target,  # first
    created_report: Report,  # second
    client: AsyncClient,
) -> None:
    response = await client.get("/targets")
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 1

    got = Target(**json[0])

    # reassure mypy
    assert created_target.current is not None
    assert created_report.count is not None

    updated_count = created_target.current + created_report.count

    assert got.current == updated_count
    assert got.completed == (updated_count == created_target.target)
