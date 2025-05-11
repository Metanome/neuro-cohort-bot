from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
import os

# Set up the scheduler for periodic data collection and log cleanup
def setup_scheduler(data_collection_function, log_cleanup_days=30):
    scheduler = BackgroundScheduler()
    scheduler.add_job(data_collection_function, 'interval', minutes=30, id='data_collection_job')
    logging.info(f'Scheduler set up to run every 30 minutes at {datetime.now()}')
    # Optional: schedule log cleanup
    scheduler.add_job(lambda: cleanup_old_logs('logs', log_cleanup_days), 'cron', hour=0, minute=0, id='log_cleanup_job')
    scheduler.start()
    return scheduler

# Delete log files older than a certain number of days
def cleanup_old_logs(log_dir, days=30):
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime < cutoff:
                try:
                    os.remove(file_path)
                    logging.info(f"Deleted old log file: {file_path}")
                except Exception as e:
                    logging.warning(f"Failed to delete log file {file_path}: {e}")
    # TODO: Make log directory and retention configurable via config if needed