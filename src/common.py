from datetime import datetime


def limit_is_expired(limit: int) -> bool:
    return limit <= datetime.now().timestamp()
