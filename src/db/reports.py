from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.model.report import (
    CreateReport,
    Report,
)
from src.common import TargetType
from src.db.model.report import DBReport
import src.db.targets as targets_db


async def get_reports(
    session: AsyncSession,
    user: int,
    type: Optional[TargetType],
    start: Optional[datetime],
    end: Optional[datetime],
) -> List[Report]:
    query = select(DBReport).filter_by(author=user)

    if type is not None:
        query = query.filter_by(type=type)

    if start is not None:
        query = query.filter(DBReport.date >= start)

    if end is not None:
        query = query.filter(DBReport.date <= end)

    res = await session.scalars(query)
    reports = res.all()

    return list(map(DBReport.to_api, reports))


async def create_report(
    session: AsyncSession, author: int, report: CreateReport
) -> Report:
    new_report = DBReport(**report.dict(), author=author)

    # to reassure mypy
    assert report.type is not None
    assert report.count is not None

    await targets_db.update_targets(session, author, report.type, report.count)

    session.add(new_report)
    await session.commit()

    return new_report.to_api()
