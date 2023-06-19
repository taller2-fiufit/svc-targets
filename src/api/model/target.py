from typing import Any, Dict, Optional
from fastapi import Query
from pydantic import BaseModel, Field, root_validator
from src.api.model.utils import OrmModel, make_all_required


class TargetBase(OrmModel):
    name: Optional[str] = Field(
        title="Name",
        description="The target's name",
        min_length=2,
        max_length=30,
        default=None,
    )
    description: Optional[str] = Field(
        title="Description",
        description="The target's description",
        max_length=300,
        default=None,
    )
    limit: Optional[int] = Field(
        title="Time limit",
        description="The target's time limit. "
        "After this date, the target can't be completed",
        default=None,
    )
    current: Optional[float] = Field(
        title="Current progress",
        description="The target's current progress",
        ge=0.0,
        default=None,
    )
    target: Optional[float] = Field(
        title="Target progress",
        description="The target's progress goal. "
        "The target is considered completed when the"
        " current progress reaches this value.",
        ge=0.0,
        default=None,
    )
    unit: Optional[str] = Field(
        title="Unit",
        description="The target's progress unit. "
        "E.g.: 'kg', 'km', 'm', 'cm', 'h', 'min', 's', etc.",
        max_length=30,
        default=None,
    )


class AllRequiredTargetBase(TargetBase):
    @root_validator()
    def validate_current_le_target(
        cls, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        if fields["current"] is not None and fields["target"] is not None:
            assert fields["current"] <= fields["target"], (
                f"Current progress ({fields['current']}) must be "
                f"less than target progress ({fields['target']})"
            )
        return fields


make_all_required(AllRequiredTargetBase)


class CreateTarget(AllRequiredTargetBase):
    pass


class PatchTarget(TargetBase):
    pass


class Target(AllRequiredTargetBase):
    id: int = Field(title="ID", description="The target's ID")


class FilterParams(BaseModel):
    offset: int = Field(Query(0, title="Query initial offset"))
    limit: int = Field(Query(100, title="Query item limit"))
