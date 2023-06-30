from datetime import datetime
from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    Integer,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.api.model.report import Report
from src.db.model.base import Base
from src.common import TargetType


class DBReport(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author: Mapped[int] = mapped_column(Integer)
    type: Mapped[TargetType] = mapped_column(Enum(TargetType))
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    count: Mapped[float] = mapped_column(Float(9))

    def to_api(self) -> Report:
        return Report(
            type=self.type,
            count=self.count,
        )
