"""
Logging configuration module for the Neuro Cohort Bot.

This module sets up a rotating file logger with console output
to keep track of the bot's operation and help with debugging.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

# Default configuration
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "neuroscience_bot.log"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s [%(levelname)s]: %(message)s'
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
DEFAULT_BACKUP_COUNT = 5

def setup_logger(log_dir=DEFAULT_LOG_DIR, 
                 log_file=DEFAULT_LOG_FILE,
                 log_level=DEFAULT_LOG_LEVEL,
                 log_format=DEFAULT_LOG_FORMAT,
                 max_bytes=DEFAULT_MAX_BYTES,
                 backup_count=DEFAULT_BACKUP_COUNT,
                 console_output=True):
    """
    Set up a rotating file logger with optional console output.
    
    Args:
        log_dir (str): Directory to store log files
        log_file (str): Name of the log file
        log_level (int): Logging level (e.g., logging.INFO)
        log_format (str): Format string for log messages
        max_bytes (int): Maximum size in bytes before rotating
        backup_count (int): Number of backup files to keep
        console_output (bool): Whether to also log to console
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create formatter
    log_formatter = logging.Formatter(log_format)
    
    # Ensure logs directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created logs directory: {log_dir}")
    
    # Get the full log file path
    log_path = os.path.join(log_dir, log_file)
    
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set up file handler for rotating logs
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
    
    logging.info("Logger initialized successfully")
    return logger