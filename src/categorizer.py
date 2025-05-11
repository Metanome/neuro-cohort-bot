# Categorize data items into predefined categories
def categorize_data(data_items):
    categories = {
        'news': [],
        'events': [],
        'jobs': [],
        'videos/courses': [],
        'facts': []
    }
    for item in data_items:
        category = item.get('category')
        if category in categories:
            categories[category].append(item)
        # TODO: Handle unknown categories if needed
    return categories