from typing import List, Optional
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.api.model.target import CreateTarget, Multimedia, Target
from src.db.model.base import Base


class DBMultimedia(Base):
    __tablename__ = "target_multimedias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id"))
    url: Mapped[str] = mapped_column(String(255))


def multimedia_api_to_db(multimedia: List[Multimedia]) -> List[DBMultimedia]:
    return [DBMultimedia(url=str(m)) for m in multimedia]


def multimedia_db_to_api(
    multimedia: List[DBMultimedia],
) -> List[Multimedia]:
    return [Multimedia(m.url) for m in multimedia]


class DBTarget(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    author: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(300))
    limit: Mapped[int] = mapped_column(Integer)  # in seconds
    current: Mapped[float] = mapped_column(Float(9))
    target: Mapped[float] = mapped_column(Float(9))
    unit: Mapped[str] = mapped_column(String(30))
    multimedia: Mapped[List[DBMultimedia]] = relationship(
        cascade="all, delete-orphan",
        lazy="immediate",
    )

    @classmethod
    def from_api_model(
        cls,
        author: int,
        target: CreateTarget,
    ) -> "DBTarget":
        # this never happens, but mypy needs reassurance
        assert target.multimedia is not None

        db_multimedia = multimedia_api_to_db(target.multimedia)

        kwargs = {
            **target.dict(),
            "limit": target.limit // 1000,  # from ms
            "multimedia": db_multimedia,
        }

        return cls(author=author, **kwargs)

    def to_api_model(self) -> Target:
        multimedia = multimedia_db_to_api(self.multimedia)

        return Target(
            id=self.id,
            name=self.name,
            description=self.description,
            limit=self.limit * 1000,  # to ms
            current=self.current,
            target=self.target,
            unit=self.unit,
            multimedia=multimedia,
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        limit: Optional[int] = None,
        current: Optional[float] = None,
        target: Optional[float] = None,
        unit: Optional[str] = None,
        multimedia: Optional[List[Multimedia]] = None,
    ) -> None:
        """Conditionally updates the targets attributes."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if limit is not None:
            self.limit = limit // 1000  # from ms
        if current is not None:
            self.current = current
        if target is not None:
            self.target = target
        if unit is not None:
            self.unit = unit
        if multimedia is not None:
            self.multimedia = multimedia_api_to_db(multimedia)

        if self.current > self.target:
            self.current = self.target
