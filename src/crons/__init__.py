from apscheduler.schedulers.background import BackgroundScheduler

from src.crons.add_focus_to_chroma import refresh_focus_from_chroma

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.start()
    # scheduler.add_job(upsert_focus_to_pinecone, "interval", minutes=1)
    scheduler.add_job(refresh_focus_from_chroma, "interval", minutes=1)


def shutdown_scheduler():
    scheduler.shutdown()
