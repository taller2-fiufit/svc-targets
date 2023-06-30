from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.model.report import (
    CreateReport,
    Report,
)
from src.api.model.target import Target
from src.common import TargetType
from src.db.model.report import DBReport
import src.db.targets as targets_db


async def get_reports(
    session: AsyncSession,
    user: int,
    start: Optional[datetime],
    end: Optional[datetime],
) -> List[Report]:
    query = select(DBReport).filter_by(author=user)

    if start is not None:
        query = query.filter(DBReport.date >= start)

    if end is not None:
        query = query.filter(DBReport.date <= end)

    res = await session.scalars(query)

    reports = {v: Report(type=v, count=0) for v in TargetType}

    for report in res.all():
        reports[report.type].count = (reports[report.type].count or 0) + (
            report.count or 0
        )

    return list(reports.values())


async def create_report(
    session: AsyncSession, author: int, report: CreateReport
) -> Tuple[Report, List[Target]]:
    new_report = DBReport(type=report.type, count=report.count, author=author)

    # to reassure mypy
    assert report.type is not None
    assert report.count is not None

    completed = await targets_db.update_targets(
        session, author, report.type, report.count
    )

    session.add(new_report)
    await session.commit()

    return new_report.to_api(), completed
