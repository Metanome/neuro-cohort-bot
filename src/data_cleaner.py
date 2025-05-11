def clean_data(data):
    seen = set()
    cleaned_data = []
    for item in data:
        identifier = item.get('id') or item.get('title')
        if identifier and identifier not in seen:
            seen.add(identifier)
            cleaned_data.append(item)
    cleaned_data = [item for item in cleaned_data if is_relevant(item)]
    return cleaned_data

def is_relevant(item):
    # Filter out items missing title or url
    if not item.get('title') or not item.get('url'):
        return False
    # Add more custom rules as needed
    return True