from datetime import datetime


def limit_is_expired(limit) -> bool:
    return limit > datetime.now().timestamp()