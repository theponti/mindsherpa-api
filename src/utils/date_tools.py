from datetime import datetime, time
from typing import Optional


def date_to_iso(date: datetime | str | None) -> Optional[str]:
    if isinstance(date, datetime):
        return date.isoformat()

    if isinstance(date, str):
        return date

    return None


def get_start_of_today():
    today = datetime.now().date()
    start_of_today = datetime.combine(today, time(0, 0, 0))
    return start_of_today


def get_end_of_today():
    today = datetime.now().date()
    end_of_today = datetime.combine(today, time(23, 59, 59))
    return end_of_today


def get_datetime_from_string(date_string: datetime | str | None) -> Optional[datetime]:
    if isinstance(date_string, datetime):
        return date_string

    if not date_string or not isinstance(date_string, str):
        return None

    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
