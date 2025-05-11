import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    log_file = "logs/neuroscience_bot.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)