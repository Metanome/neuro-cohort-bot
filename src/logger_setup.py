import logging
from logging.handlers import RotatingFileHandler

# Set up rotating file logger
def setup_logger():
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')  # Define log message format
    log_file = "logs/neuroscience_bot.log"  # Log file path
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)  # Set up rotating file handler
    file_handler.setFormatter(log_formatter)  # Apply formatter to file handler

    logger = logging.getLogger()  # Get the root logger
    logger.setLevel(logging.INFO)  # Set logging level to INFO
    logger.addHandler(file_handler)  # Add file handler to logger
    # TODO: Make log file path and log level configurable if needed