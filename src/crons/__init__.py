from apscheduler.schedulers.background import BackgroundScheduler

from src.crons.add_focus_to_chroma import add_focus_to_vector_store_job

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.start()
    scheduler.add_job(func=add_focus_to_vector_store_job, trigger="interval", seconds=60)


def shutdown_scheduler():
    scheduler.shutdown()
