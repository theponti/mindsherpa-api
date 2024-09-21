from datetime import datetime, time
from typing import Optional


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
