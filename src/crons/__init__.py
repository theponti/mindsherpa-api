from apscheduler.schedulers.background import BackgroundScheduler

from src.crons.focus_crons import delete_none_ids_from_chroma, refresh_focus_from_chroma

scheduler = BackgroundScheduler()


def start_scheduler():
    delete_none_ids_from_chroma()
    refresh_focus_from_chroma()
    # scheduler.start()
    # scheduler.add_job(delete_none_ids_from_chroma, "interval", minutes=5)
    # scheduler.add_job(refresh_focus_from_chroma, "interval", minutes=1)


def shutdown_scheduler():
    scheduler.shutdown()
