from datetime import datetime, timedelta
from httpx import AsyncClient
from http import HTTPStatus

from src.api.model.report import Report
from src.common import TargetType


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
    assert len(json) == 1

    got = Report(**json[0])

    assert got == created_report


async def test_reports_type_filters(
    check_empty_reports: None, created_report: Report, client: AsyncClient
) -> None:
    other_type = TargetType.TIME_SPENT
    assert created_report.type != other_type
    response = await client.get("/reports", params={"type": str(other_type)})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []

    response = await client.get(
        "/reports", params={"type": str(created_report.type)}
    )
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 1

    got = Report(**json[0])

    assert got == created_report


async def test_reports_date_filters(
    check_empty_reports: None, created_report: Report, client: AsyncClient
) -> None:
    # [start, end] doesn't include created_report.date
    start = datetime.utcnow() - timedelta(minutes=10)
    end = datetime.utcnow() - timedelta(minutes=5)
    params = {"start": start.isoformat(), "end": end.isoformat()}
    response = await client.get("/reports", params=params)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []

    # [start, end] does include created_report.date
    params["end"] = datetime.utcnow().isoformat()

    response = await client.get("/reports", params=params)
    assert response.status_code == HTTPStatus.OK
    json = response.json()
    assert len(json) == 1

    got = Report(**json[0])

    assert got == created_report
