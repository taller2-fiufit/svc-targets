from http import HTTPStatus
from typing import List, Annotated
from fastapi import APIRouter, BackgroundTasks, Depends

from src.api.model.report import CreateReport, Report, ReportParams
from src.api.model.target import Target
from src.api.aliases import SessionDep, UserDep
from src.auth import get_user
from src.db.utils import get_session
from src.logging import info
import src.db.reports as reports_db


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    # List of dependencies that get run ALWAYS for router and subrouters.
    # For a single-route dependency use the route decorator's parameter "dependencies"
    dependencies=[Depends(get_session), Depends(get_user)],
)

Filters = Annotated[ReportParams, Depends()]


def send_push(
    token: str,
    completed: List[Target]
) -> None:
    pass


@router.get("")
async def get_reports(
    session: SessionDep,
    user: UserDep,
    f: Filters,
) -> List[Report]:
    """Get all the user's reports"""
    return await reports_db.get_reports(
        session,
        user.sub,
        f.type,
        f.get_start(),
        f.get_end(),
    )


@router.post("", status_code=HTTPStatus.CREATED)
async def post_report(
    session: SessionDep,
    user: UserDep,
    report: CreateReport,
    background_tasks: BackgroundTasks,
) -> Report:
    """Create a new report"""
    new_report, completed = await reports_db.create_report(session, user.sub, report)
    info(f"New report created: {new_report}")
    if report.token is not None:
        background_tasks.add_task(send_push, report.token, completed)
    return new_report
