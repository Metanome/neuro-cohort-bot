"""
Data cleaning module for the Neuro Cohort Bot.

This module handles deduplication of items and filtering of irrelevant content
before it's categorized and sent to Telegram.
"""

def clean_data(data):
    """
    Deduplicate and filter irrelevant data items.
    
    Args:
        data (list): Raw data items fetched from various sources
        
    Returns:
        list: Deduplicated and filtered list of data items
    """
    seen = set()  # Track unique identifiers
    cleaned_data = []
    
    # First pass: deduplicate by identifier
    for item in data:
        identifier = item.get('id') or item.get('title')  # Use 'id' or 'title' as unique identifier
        if identifier and identifier not in seen:
            seen.add(identifier)  # Track seen identifiers to avoid duplicates
            cleaned_data.append(item)  # Add unique item to cleaned data
            
    # Second pass: filter out irrelevant items
    cleaned_data = [item for item in cleaned_data if is_relevant(item)]
    
    return cleaned_data

def is_relevant(item):
    """
    Check if an item is relevant for inclusion.
    
    Args:
        item (dict): Data item to check
        
    Returns:
        bool: True if the item is relevant, False otherwise
    """
    # Basic check: filter out items missing title or url
    if not item.get('title') or not item.get('url'):
        return False
    
    # Add more custom rules as needed, such as:
    # - Filter by keywords in title or description
    # - Check for minimum content length
    # - Verify source credibility
    
    return True