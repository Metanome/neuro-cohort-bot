"""
Pagination utility functions for DataFetcher

This module provides functions for paginating through content on websites
and handling extracted data consistently.
"""
import logging
import time
from bs4 import BeautifulSoup
from src.http_utils import http_get

def paginate_website(base_url, max_pages, page_selector, item_processor, page_delay=2, item_delay=1):
    """
    Fetch and process paginated content from a website.
      Args:
        base_url (str): The base URL to paginate from
        max_pages (int): Maximum number of pages to fetch
        page_selector: CSS selector string or function to find items on each page
        item_processor (callable): Function to process each found item
        page_delay (int): Delay in seconds between page requests
        item_delay (int): Delay in seconds between item processing
            
    Returns:
        tuple: (list of items found across all pages, number of pages processed)
    """
    items = []
    base_url = base_url.rstrip('/')  # Remove trailing slash if present
    current_page = 1
    
    # Fetch additional pages
    while current_page < max_pages:
        current_page += 1
        
        # Add a delay between page requests
        time.sleep(page_delay)
        
        next_page_url = f"{base_url}/page/{current_page}/"
        logging.info(f"Fetching page {current_page} from {next_page_url}")
        
        try:
            next_page_response = http_get(next_page_url, timeout=10, retries=2)
            
            if not next_page_response or next_page_response.status_code != 200:
                logging.warning(f"Failed to fetch page {current_page}")
                break
                
            next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')
            
            # If page_selector is a function, call it with the soup
            if callable(page_selector):
                next_page_items = page_selector(next_page_soup)
            else:
                next_page_items = next_page_soup.find_all(page_selector)
            
            logging.info(f"Found {len(next_page_items)} items on page {current_page}")
            
            # Process items from this page
            for idx, item in enumerate(next_page_items):
                if idx > 0:
                    time.sleep(item_delay)  # Delay between items
                    
                processed_item = item_processor(item, idx, current_page)
                if processed_item:
                    items.append(processed_item)
                    
        except Exception as e:
            logging.warning(f"Error processing page {current_page}: {e}")
            break
            
    return items, current_page
