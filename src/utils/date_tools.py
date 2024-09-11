from datetime import datetime, time


def get_end_of_today():
    today = datetime.now().date()
    end_of_today = datetime.combine(today, time(23, 59, 59))
    return end_of_today
