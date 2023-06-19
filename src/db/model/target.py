from typing import Optional
from sqlalchemy import (
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db.model.base import Base


class DBTarget(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(300))
    limit: Mapped[int] = mapped_column(Integer)
    current: Mapped[float] = mapped_column(Float(9))
    target: Mapped[float] = mapped_column(Float(9))
    unit: Mapped[str] = mapped_column(String(30))

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        limit: Optional[int] = None,
        current: Optional[float] = None,
        target: Optional[float] = None,
        unit: Optional[str] = None,
    ) -> None:
        """Conditionally updates the targets attributes."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if limit is not None:
            self.limit = limit
        if current is not None:
            self.current = current
        if target is not None:
            self.target = target
        if unit is not None:
            self.unit = unit

        if self.current > self.target:
            self.current = self.target
