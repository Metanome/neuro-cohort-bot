"""
Message formatting module for the Neuro Cohort Bot.

This module handles formatting data items into Telegram-compatible messages,
tracking already posted URLs to prevent duplicates, and ensuring messages
comply with Telegram's markdown formatting requirements.
"""
import os
import time
import logging
import urllib.parse
from datetime import datetime, timedelta
from src.utils import handle_error, make_url_absolute

# File to track posted URLs with timestamps
POSTED_URLS_FILE = os.path.join(os.path.dirname(__file__), '../posted_urls.txt')  

# Maximum age for URLs in days (default: 90 days)
URL_RETENTION_DAYS = 90

# Maximum URLs to store in file
MAX_STORED_URLS = 5000

def load_posted_urls():
    """Load posted URLs from file and filter out expired ones"""
    if not os.path.exists(POSTED_URLS_FILE):
        return set()
    
    posted_urls = set()
    try:
        with open(POSTED_URLS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line contains timestamp (format: URL|timestamp)
                if '|' in line:
                    url, timestamp_str = line.rsplit('|', 1)
                    # Only include URLs that aren't expired
                    try:
                        if not _is_url_expired(float(timestamp_str)):
                            posted_urls.add(url)
                    except ValueError:
                        posted_urls.add(line)  # Fall back to adding the whole line if timestamp is invalid
                else:
                    posted_urls.add(line)  # Handle old format URLs (without timestamp)
        
        # Purge file if needed
        if len(posted_urls) > MAX_STORED_URLS:
            logging.info(f"URL file exceeded max size ({len(posted_urls)}). Purging old URLs...")
            _purge_old_urls()
            
        return posted_urls
    except Exception as e:
        logging.error(f"Error loading posted URLs: {e}")
        return set()

def save_posted_url(url):
    """Save a URL with the current timestamp"""
    try:
        with open(POSTED_URLS_FILE, 'a', encoding='utf-8') as f:
            timestamp = time.time()
            f.write(f"{url}|{timestamp}\n")  # Append new posted URL with timestamp
    except Exception as e:
        logging.error(f"Error saving posted URL: {e}")

def _is_url_expired(timestamp):
    """Check if a URL timestamp is older than the retention period"""
    cutoff = time.time() - (URL_RETENTION_DAYS * 24 * 60 * 60)
    return timestamp < cutoff

def _purge_old_urls():
    """Purge old URLs from file, keeping only the most recent ones"""
    try:
        if not os.path.exists(POSTED_URLS_FILE):
            return
            
        # Read all URLs with timestamps
        urls_with_timestamps = []
        with open(POSTED_URLS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse timestamp or set to 0 if not present
                if '|' in line:
                    url, timestamp_str = line.rsplit('|', 1)
                    try:
                        timestamp = float(timestamp_str)
                        urls_with_timestamps.append((url, timestamp))
                    except ValueError:
                        urls_with_timestamps.append((line, 0))
                else:
                    urls_with_timestamps.append((line, 0))
        
        # Sort by timestamp (newest first) and keep only the MAX_STORED_URLS newest
        urls_with_timestamps.sort(key=lambda x: x[1], reverse=True)
        urls_to_keep = urls_with_timestamps[:MAX_STORED_URLS]
        
        # Write back the newest URLs
        with open(POSTED_URLS_FILE, 'w', encoding='utf-8') as f:
            for url, timestamp in urls_to_keep:
                f.write(f"{url}|{timestamp}\n")
                
        logging.info(f"URL purge complete. Kept {len(urls_to_keep)} of {len(urls_with_timestamps)} URLs.")
    except Exception as e:
        logging.error(f"Error purging old URLs: {e}")

def escape_markdown_v2(text):
    """Escape Telegram MarkdownV2 special characters in visible text only."""
    if not text:
        return ''
    escape_chars = r'_[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def format_research_info(orig_research_title, orig_research_url, orig_research, article_url):
    """Format research information for Telegram message
    
    Args:
        orig_research_title: Title of the original research paper
        orig_research_url: URL of the original research paper
        orig_research: String with research info
        article_url: URL of the current article (for relative URL resolution)
        
    Returns:
        str: Formatted research information line or empty string
    """
    
    if orig_research_title and orig_research_url:
        # Ensure the URL is absolute and properly formatted
        orig_research_url = make_url_absolute(orig_research_url, article_url)

        # Make sure the URL is properly formatted for Markdown - escape special characters in URLs
        safe_url = orig_research_url.replace(")", "\\)").replace("(", "\\(")
        return f"📝 *Research:* [{orig_research_title}]({safe_url})"
    elif orig_research_title:
        # We have a title but no URL
        return f"📝 *Research:* {orig_research_title}"
    elif orig_research:
        # Fallback to the full string (already using "Research:" format)
        return f"📝 {orig_research}"
    return ""

def get_and_format_description(item):
    """Extract and format a description from an item
    
    Args:
        item: Dictionary containing article data
        
    Returns:
        str: Formatted and escaped description ready for Markdown, or empty string if no description
    """
    
    # Get description from the item
    desc = item.get('description', '')
    
    # Try to get description from item with different keys if needed
    if not desc or desc.strip() == '':
        for key in ['desc', 'summary', 'content', 'excerpt']:
            if item.get(key) and item.get(key).strip() != '':
                desc = item.get(key)
                logging.debug(f"Found description under key '{key}'")
                break
                
    # Clean up the description if needed
    if desc and desc.strip() != '':
        # Sometimes descriptions might still have "Summary: " at the beginning
        if desc.startswith("Summary:"):
            desc = desc[len("Summary:"):].strip()
        
        # Strip out HTML tags that might have been missed
        desc = desc.replace("<strong>Summary:</strong>", "").replace("<strong>", "").replace("</strong>", "")
        
        # Make sure we escape the description properly for Markdown
        escaped_desc = escape_markdown_v2(desc)
        
        # Limit to a reasonable length (around 2-3 sentences)
        max_chars = 500
        if len(escaped_desc) > max_chars:
            # Try to cut at a sentence ending
            cut_point = escaped_desc[:max_chars].rfind('.')
            if cut_point > max_chars * 0.6:  # Only cut at sentence if we're getting most of the text
                escaped_desc = escaped_desc[:cut_point + 1]
        
        return escaped_desc
    
    return ""

# Format categorized data into a Markdown message for Telegram
def format_message(data):
    posted_urls = load_posted_urls()
    messages = []  # Collect all formatted messages
    for category, items in data.items():
        for item in items:
            url = item.get('url', '')
            if not url or url in posted_urls:
                continue  # Skip already posted or missing URL
            title = escape_markdown_v2(item.get('title', 'No Title'))  # Escape only visible text
            description = escape_markdown_v2(item.get('description', '')) if item.get('description') else None
            author_name = escape_markdown_v2(item.get('author')) if item.get('author') else None
            source_label = escape_markdown_v2(item.get('source_label')) if item.get('source_label') else None
            orig_research = escape_markdown_v2(item.get('original_research')) if item.get('original_research') else None
            orig_research_url = item.get('original_research_url')
            orig_research_title = escape_markdown_v2(item.get('original_research_title')) if item.get('original_research_title') else None
            
            # Debug log for tracking research data and description
            if orig_research or orig_research_title or orig_research_url:
                logging.debug(f"Message formatting - Research: '{orig_research_title}' URL: {orig_research_url}, Raw: {orig_research}")
            
            # Remove the temporary debugging log once we've confirmed it works
            
            # Format the date in a human-readable way
            date_str = item.get('date')
            if date_str:
                try:
                    # Parse ISO format date (2025-05-15T13:25:41-07:00)
                    dt = datetime.fromisoformat(date_str)
                    # Format as "May 15, 2025"
                    formatted_date = dt.strftime("%B %d, %Y")
                    date = escape_markdown_v2(formatted_date)
                except ValueError:
                    # If parsing fails, use the original string
                    date = escape_markdown_v2(date_str)
            else:
                date = None
            message = f"*{title}*\n"
            message += "\n"
            
            # Add description/summary right after the title
            desc = get_and_format_description(item)
            if desc:
                message += f"{desc}\n\n"
                logging.debug(f"Added description to message ({len(desc)} chars)")
            else:
                logging.debug("No description available for this article")
                
            if author_name:
                message += f"*👤 Author:* {author_name}\n"
            if date:
                message += f"*🗓 Date:* {date}\n"
            if source_label:
                message += f"*📌 Source:* {source_label}\n"
                
            # Handle original research with proper formatting - placed right after source
            research_line = format_research_info(orig_research_title, orig_research_url, orig_research, url)
            if research_line:
                message += f"{research_line}\n"
                
            message += "\n"
            # Only escape the visible text, not the URL
            message += f"[📖 Read Article]({url})\n"
            messages.append((message.strip(), url))  # Add to the list instead of returning immediately
    return messages