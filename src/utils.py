"""
Utility functions for the Neuro Cohort Bot.

This module contains common utility functions used across the application.
"""
import logging
import os
import traceback
import urllib.parse
from datetime import datetime, timedelta

def cleanup_old_logs(log_dir, days=30):
    """
    Delete log files older than a certain number of days.
    
    Args:
        log_dir (str): Directory containing the log files
        days (int): Number of days to keep log files, older files will be deleted
        
    Returns:
        int: Number of files deleted
    """
    if not os.path.exists(log_dir):
        logging.warning(f"Log directory {log_dir} does not exist. Skipping cleanup.")
        return 0
        
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    count = 0
    
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mtime < cutoff:
                try:
                    os.remove(file_path)
                    count += 1
                    logging.info(f"Deleted old log file: {file_path}")
                except Exception as e:
                    logging.warning(f"Failed to delete log file {file_path}: {e}")
    
    if count > 0:
        logging.info(f"Log cleanup completed: {count} old log files deleted.")
    
    return count

def make_url_absolute(relative_url, base_url):
    """
    Convert a relative URL to an absolute URL.
    
    Args:
        relative_url (str): The relative URL to convert
        base_url (str): The base URL to use for conversion
        
    Returns:
    str: The absolute URL
    """
    
    if relative_url.startswith(('http://', 'https://')):
        return relative_url
    
    try:
        base_parts = urllib.parse.urlparse(base_url)
        base = f"{base_parts.scheme}://{base_parts.netloc}"
        return urllib.parse.urljoin(base, relative_url)
    except Exception as e:
        logging.warning(f"Error converting relative URL to absolute: {e}")
        return relative_url
        
def handle_error(error, error_type="general", with_traceback=True):
    """
    Handle and log errors consistently.
    
    Args:
        error (Exception): The error to handle
        error_type (str): The type of operation that failed
        with_traceback (bool): Whether to include traceback information
        
    Returns:
        str: The formatted error message
    """
    error_msg = f"Error in {error_type}: {str(error)}"
    
    if with_traceback:
        logging.error(f"{error_msg}\n{traceback.format_exc()}")
    else:
        logging.error(error_msg)
        
    return error_msg

def safely_execute(func, args=None, kwargs=None, error_type="operation", default_return=None):
    """
    Execute a function safely, handling any exceptions.
    
    Args:
        func (callable): Function to execute
        args (tuple, optional): Positional arguments to pass to the function
        kwargs (dict, optional): Keyword arguments to pass to the function
        error_type (str): The type of operation being performed (for error reporting)
        default_return: Value to return if an error occurs
        
    Returns:
        The return value from the function, or default_return if an error occurred
    """
    args = args or ()
    kwargs = kwargs or {}
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, error_type)
        return default_return
