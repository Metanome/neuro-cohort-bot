def format_message(data):
    message_parts = []
    category_titles = {
        'news': '📰 News',
        'events': '📅 Events',
        'jobs': '💼 Jobs',
        'videos/courses': '🎥 Videos & Courses',
        'facts': '🧠 Facts'
    }
    for category, items in data.items():
        if items:
            message_parts.append(f"*{category_titles.get(category, category.capitalize())}*:\n")
            for item in items:
                title = item.get('title', 'No Title')
                url = item.get('url', '')
                desc = item.get('description', '')
                line = f"- [{title}]({url})"
                if desc:
                    line += f"\n    _{desc}_"
                message_parts.append(line + "\n")
            message_parts.append("\n")
    return ''.join(message_parts).strip()