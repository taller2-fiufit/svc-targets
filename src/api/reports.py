from http import HTTPStatus
from typing import List, Annotated
from fastapi import APIRouter, Depends

from src.api.model.report import CreateReport, Report, ReportParams
from src.api.aliases import SessionDep, UserDep
from src.auth import get_user
from src.db.utils import get_session
from src.logging import info
from datetime import datetime
import src.db.reports as reports_db


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    # List of dependencies that get run ALWAYS for router and subrouters.
    # For a single-route dependency use the route decorator's parameter "dependencies"
    dependencies=[Depends(get_session), Depends(get_user)],
)

Filters = Annotated[ReportParams, Depends()]


@router.get("")
async def get_reports(
    session: SessionDep,
    user: UserDep,
    f: Filters,
) -> List[Report]:
    """Get all the user's reports"""
    start = datetime.fromisoformat(f.start).astimezone() if f.start else None
    end = datetime.fromisoformat(f.end).astimezone() if f.end else None
    return await reports_db.get_reports(
        session,
        user.sub,
        f.type,
        start,
        end,
    )


@router.post("", status_code=HTTPStatus.CREATED)
async def post_report(
    session: SessionDep,
    user: UserDep,
    training: CreateReport,
) -> Report:
    """Create a new report"""
    new_report = await reports_db.create_report(session, user.sub, training)
    info(f"New report created: {new_report}")
    return new_report
