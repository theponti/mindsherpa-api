from apscheduler.schedulers.background import BackgroundScheduler

from src.services.pinecone_service import upsert_focus_to_pinecone

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.start()
    scheduler.add_job(upsert_focus_to_pinecone, "interval", minutes=1)


def shutdown_scheduler():
    scheduler.shutdown()
