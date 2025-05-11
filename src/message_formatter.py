def format_message(data):
    message_parts = []

    for category, items in data.items():
        if items:
            message_parts.append(f"*{category.capitalize()}*:\n")
            for item in items:
                message_parts.append(f"- {item}\n")
            message_parts.append("\n")

    return ''.join(message_parts).strip()