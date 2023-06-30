from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
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
    start: Optional[datetime],
    end: Optional[datetime],
) -> List[Report]:
    query = (
        select(DBReport, func.sum(DBReport.count))
        .group_by(DBReport.type)
        .filter_by(author=user)
    )

    if start is not None:
        query = query.filter(DBReport.date >= start)

    if end is not None:
        query = query.filter(DBReport.date <= end)

    res = await session.execute(query)

    reports = [Report(type=r[0].type, count=r[1]) for r in res.all()]
    types = [r.type for r in reports]

    for v in TargetType:
        if v not in types:
            reports.append(Report(type=v, count=0))

    return reports


async def create_report(
    session: AsyncSession, author: int, report: CreateReport
) -> Report:
    new_report = DBReport(type=report.type, count=report.count, author=author)

    # to reassure mypy
    assert report.type is not None
    assert report.count is not None

    await targets_db.update_targets(session, author, report.type, report.count)

    session.add(new_report)
    await session.commit()

    return new_report.to_api()
