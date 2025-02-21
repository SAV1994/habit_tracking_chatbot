from datetime import datetime

import pytz

from app.settings import TZ


def aware_now() -> datetime:
    return datetime.now(pytz.timezone(TZ))
