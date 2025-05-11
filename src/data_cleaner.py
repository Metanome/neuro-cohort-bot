def clean_data(data):
    seen = set()
    cleaned_data = []

    for item in data:
        # Assuming each item is a dictionary with a unique 'id' or 'title'
        identifier = item.get('id') or item.get('title')
        if identifier not in seen:
            seen.add(identifier)
            cleaned_data.append(item)

    # Further cleaning logic can be added here, such as removing irrelevant entries
    # For example, filtering out items based on certain criteria
    cleaned_data = [item for item in cleaned_data if is_relevant(item)]

    return cleaned_data

def is_relevant(item):
    # Placeholder for relevance check logic
    # This can be customized based on specific criteria for relevance
    return True  # Modify this as needed to filter out irrelevant entries