"""
Content categorization module for the Neuro Cohort Bot.

This module organizes content items into predefined categories
to make them easier to manage and display in the Telegram channel.
"""
import logging

# Predefined content categories
DEFAULT_CATEGORIES = {
    'news': [],
    'events': [],
    'jobs': [],
    'videos/courses': [],
    'facts': []
}

def categorize_data(data_items):
    """
    Categorize data items into predefined categories based on their 'category' field.
    
    Args:
        data_items (list): List of cleaned data items to categorize
        
    Returns:
        dict: Dictionary mapping category names to lists of data items
    """
    # Initialize categories dictionary with empty lists
    categories = DEFAULT_CATEGORIES.copy()
    
    # Count for logging
    uncategorized_count = 0
    
    # Process each item
    for item in data_items:
        category = item.get('category', 'news')  # Default to 'news' if no category
        
        if category in categories:
            # Add item to its proper category
            categories[category].append(item)
        else:
            # Handle unknown categories by adding to 'news' with a warning
            categories['news'].append(item)
            uncategorized_count += 1
    
    # Log categorization results
    for category, items in categories.items():
        logging.debug(f"Categorized {len(items)} items as '{category}'")
    
    if uncategorized_count > 0:
        logging.warning(f"{uncategorized_count} items had unknown categories and were added to 'news'")
        
    return categories