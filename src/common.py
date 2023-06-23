import enum
from datetime import datetime


def limit_is_expired(limit: int) -> bool:
    return limit <= datetime.now().timestamp()


class TargetType(enum.StrEnum):
    DISTANCE_TRAVELLED = "Distance travelled"
    TIME_SPENT = "Time spent"
    CALORIES_BURNED = "Calories burned"
    TARGETS_COMPLETED = "Targets completed"
