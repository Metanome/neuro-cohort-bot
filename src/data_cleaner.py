# Deduplicate and filter irrelevant data items
def clean_data(data):
    seen = set()
    cleaned_data = []
    for item in data:
        identifier = item.get('id') or item.get('title')  # Use 'id' or 'title' as unique identifier
        if identifier and identifier not in seen:
            seen.add(identifier)  # Track seen identifiers to avoid duplicates
            cleaned_data.append(item)  # Add unique item to cleaned data
    cleaned_data = [item for item in cleaned_data if is_relevant(item)]  # Filter out irrelevant items
    return cleaned_data

# Check if an item is relevant (customize as needed)
def is_relevant(item):
    # Filter out items missing title or url
    if not item.get('title') or not item.get('url'):
        return False
    # Add more custom rules as needed
    return True
    # TODO: Implement more advanced relevance checks if needed