from datetime import datetime, timezone
from typing import Optional
from fastapi import Query
from pydantic import BaseModel, Field
from src.api.model.utils import OrmModel, make_all_required
from src.common import TargetType


class ReportBase(OrmModel):
    type: Optional[TargetType] = Field(
        title="Type",
        description="The reported metric's type. "
        "If it counts distance travelled, time spent, etc.",
        default=None,
    )
    count: Optional[float] = Field(
        title="Counted progress",
        description="The progress counted by the report.",
        ge=0.0,
        default=None,
    )


class AllRequiredReportBase(ReportBase):
    pass


make_all_required(AllRequiredReportBase)


class CreateReport(AllRequiredReportBase):
    token: Optional[str] = Field(
        title="Notifications token",
        description="A valid token for Expo's notifications API.",
        max_length=255,
        default=None,
    )
    date: Optional[str] = Field(
        title="Date",
        description="The date for the report.",
        max_length=64,
        default=None,
    )

    def get_date(self) -> Optional[datetime]:
        return parse_time(self.date)


class Report(AllRequiredReportBase):
    pass


class ReportParams(BaseModel):
    type: Optional[TargetType] = Field(
        Query(None, title="Type of the metric that's being queried")
    )
    start: Optional[str] = Field(Query(None, title="Query start date"))
    end: Optional[str] = Field(Query(None, title="Query end date"))

    def get_start(self) -> Optional[datetime]:
        return parse_time(self.start)

    def get_end(self) -> Optional[datetime]:
        return parse_time(self.end)


def parse_time(s: Optional[str]) -> Optional[datetime]:
    if s is None:
        return None
    return (
        datetime.fromisoformat(s)
        .astimezone(tz=timezone.utc)
        .replace(tzinfo=None)
    )
