from datetime import datetime, timezone


def aware_now() -> datetime:
    return datetime.now(timezone.utc)
