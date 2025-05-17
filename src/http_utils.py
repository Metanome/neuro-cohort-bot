"""
HTTP utility functions for the Neuro Cohort Bot.

This module provides robust HTTP request handling with automatic
retry logic, timeout management, and error handling to improve
reliability when fetching data from external sources.
"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 503, 504),
    session=None
):
    """
    Create a requests Session with retry logic
    
    Parameters:
    - retries: Number of retry attempts
    - backoff_factor: Factor to apply between retry attempts (wait will be: {backoff factor} * (2 ** ({number of total retries} - 1))
    - status_forcelist: HTTP status codes that should trigger a retry
    - session: Existing session to add retry logic to
    
    Returns:
    - requests.Session with retry logic
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def http_get(url, params=None, headers=None, timeout=10, retries=3):
    """
    Make an HTTP GET request with retry logic
    
    Parameters:
    - url: URL to request
    - params: Query parameters
    - headers: Request headers
    - timeout: Request timeout
    - retries: Number of retry attempts
    
    Returns:
    - Response object or None if all attempts failed
    """
    session = create_retry_session(retries=retries)
    
    try:
        response = session.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout
        )
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed request to {url} after {retries} retries: {e}")
        return None

def http_post(url, data=None, json=None, headers=None, timeout=10, retries=3):
    """
    Make an HTTP POST request with retry logic
    
    Parameters:
    - url: URL to request
    - data: Form data
    - json: JSON data
    - headers: Request headers
    - timeout: Request timeout
    - retries: Number of retry attempts
    
    Returns:
    - Response object or None if all attempts failed
    """
    session = create_retry_session(retries=retries)
    
    try:
        response = session.post(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout
        )
        return response
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed request to {url} after {retries} retries: {e}")
        return None
