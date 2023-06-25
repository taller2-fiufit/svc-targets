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
    pass


class Report(AllRequiredReportBase):
    date: str = Field(
        title="Date",
        description="The date when the report was created.",
    )


class ReportParams(BaseModel):
    type: Optional[TargetType] = Field(
        Query(None, title="Type of the metric that's being queried")
    )
    start: Optional[str] = Field(Query(None, title="Query start date"))
    end: Optional[str] = Field(Query(None, title="Query end date"))
