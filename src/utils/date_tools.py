from datetime import datetime, time
from typing import Any, Optional


def date_to_iso(date: datetime | str | None) -> Optional[str]:
    if isinstance(date, datetime):
        return date.isoformat()

    if isinstance(date, str):
        return date

    return None


def get_end_of_today():
    today = datetime.now().date()
    end_of_today = datetime.combine(today, time(23, 59, 59))
    return end_of_today


def get_datetime_from_string(date_string: Any) -> Optional[datetime]:
    if not date_string:
        return None

    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
