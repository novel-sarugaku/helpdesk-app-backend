from datetime import datetime
from zoneinfo import ZoneInfo


def get_now() -> datetime:
    tz = ZoneInfo("Asia/Tokyo")
    return datetime.now(tz)


def get_now_UTC() -> datetime:
    return datetime.now()
