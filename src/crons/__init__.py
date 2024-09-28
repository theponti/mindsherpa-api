from apscheduler.schedulers.background import BackgroundScheduler

from src.data.db import get_db
from src.services.notification_service import notify_due_tasks

scheduler = BackgroundScheduler()


def start_scheduler():
    # scheduler.add_job(delete_none_ids_from_chroma, "interval", minutes=5)
    # scheduler.add_job(func=lambda: refresh_focus_from_chroma(next(get_db())), trigger="interval", minutes=5)
    scheduler.add_job(func=lambda: notify_due_tasks(next(get_db())), trigger="interval", minutes=15)
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown()
