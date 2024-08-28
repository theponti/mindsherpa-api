import datetime
from typing import Dict, Union


def convert_due_date(due_date: Dict[str, Union[str, int]]) -> str:
    """
    Convert the due_date dictionary to a datetime string.

    **Args:**
    - due_date (Dict[str, Union[str, int]]): A dictionary containing 'month', 'day', 'year', and 'time' keys.

    **Returns:**
    - str: A formatted datetime string or a description of the relative date.
    """
    current_date = datetime.datetime.now()

    # Handle relative month values
    if isinstance(due_date["month"], int):
        if due_date["month"] == 0:
            month = current_date.month
        else:
            month = (current_date.month + due_date["month"] - 1) % 12 + 1
    else:
        month = datetime.datetime.strptime(due_date["month"], "%B").month

    # Handle relative year values
    if isinstance(due_date["year"], int):
        if due_date["year"] == 0:
            year = current_date.year
        else:
            year = current_date.year + due_date["year"]
    else:
        year = int(due_date["year"])

    # Handle relative day values
    if isinstance(due_date["day"], int):
        if due_date["day"] == 0:
            return datetime.date(year, month, current_date.day).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            day = max(due_date["day"], (current_date + datetime.timedelta(days=due_date["day"])).day)
    else:
        try:
            day = int(due_date["day"])
        except Exception:
            print(f"Invalid day: {due_date['day']}")
            day = 0

    return datetime.datetime(year, month, day).strftime("%Y-%m-%dT%H:%M:%SZ")


def datetime_to_friendly(date: datetime.datetime) -> str:
    """
    Convert a datetime object to a friendly date string.

    Args:
    date (datetime.datetime): The datetime object to convert.

    Returns:
    str: A friendly date string.
    """
    current_date = datetime.datetime.now()
    time_str = date.strftime(" at %I:%M %p")

    if date.date() == current_date.date():
        return f"Today{time_str}"
    elif date.date() == current_date.date() + datetime.timedelta(days=1):
        return f"Tomorrow{time_str}"
    elif date.date() < current_date.date() + datetime.timedelta(days=7):
        return f"{date.strftime('%A')}{time_str}"
    else:
        return f"{date.strftime('%B %d, %Y')}{time_str}"
