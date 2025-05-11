from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

def setup_scheduler(data_collection_function):
    scheduler = BackgroundScheduler()
    scheduler.add_job(data_collection_function, 'interval', minutes=30, id='data_collection_job')
    logging.info(f'Scheduler set up to run every 30 minutes at {datetime.now()}')
    scheduler.start()
    return scheduler