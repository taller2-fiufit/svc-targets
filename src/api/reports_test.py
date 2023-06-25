from httpx import AsyncClient
from http import HTTPStatus

from src.api.model.report import Report


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
