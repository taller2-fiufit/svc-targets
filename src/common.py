import enum
from datetime import datetime, timezone


def limit_is_expired(limit: datetime) -> bool:
    return limit.astimezone(tz=timezone.utc) <= datetime.utcnow()


class TargetType(enum.StrEnum):
    DISTANCE_TRAVELLED = "Distance travelled"
    TIME_SPENT = "Time spent"
    CALORIES_BURNED = "Calories burned"
    TARGETS_COMPLETED = "Targets completed"
