"""
Data fetching module for the Neuro Cohort Bot.

This module handles retrieving data from various configured sources,
including websites and APIs, with special handling for different content
structures and pagination support for neuroscience news websites.
"""
import time
import logging
from bs4 import BeautifulSoup
from src.utils import make_url_absolute, handle_error, safely_execute
from src.http_utils import http_get
from src.status_monitor import get_monitor

class DataFetcher:
    """Class responsible for fetching data from various configured sources.
    
    This class handles retrieval of data from websites (via scraping) and APIs,
    with special handling for neuroscience news articles including pagination
    support and detailed metadata extraction.
    """
    
    def __init__(self, sources):
        """Initialize the DataFetcher with configured sources
        
        Args:
            sources: List of source configurations from sources.yaml
        """
        self.sources = sources
        self._validate_api_credentials()
    
    def _validate_api_credentials(self):
        """Validate API credentials and log warnings for missing or placeholder credentials"""
        for source in self.sources:
            if source['type'] == 'api':
                params = source.get('params', {})
                for key, value in params.items():
                    # Check for missing or placeholder API keys
                    if not value or value.startswith('YOUR_') or value == 'PLACEHOLDER':
                        logging.warning(f"Invalid API credential detected for {source['name']}: {key}={value}. This source may not work correctly.")
    
    def fetch_data(self):
        """Fetch data from all configured sources
        
        Returns:
            list: List of all fetched items from all sources
        """
        all_data = []
        
        for source in self.sources:
            try:
                if source['type'] == 'website':
                    data = self._fetch_from_website(source)  # Website parser
                elif source['type'] == 'api':
                    # Skip API sources with invalid credentials
                    if self._has_valid_credentials(source):
                        data = self._fetch_from_api(source)  # API parser
                    else:
                        logging.warning(f"Skipping {source['name']} due to invalid API credentials")
                        continue
                else:
                    logging.warning(f"Unknown source type: {source['type']} for {source.get('name')}")
                    data = []
                
                # Add category and source name to each item if not already present
                for item in data:
                    if not item.get('category'):
                        item['category'] = source.get('category')
                    if not item.get('source'):
                        item['source'] = source.get('name')
                
                all_data.extend(data)
                logging.info(f"Fetched {len(data)} items from {source.get('name')}")
                
            except Exception as e:
                logging.error(f"Error fetching data from {source.get('name')}: {e}")
                # Continue with other sources even if one fails
                
        return all_data
        
    def _has_valid_credentials(self, source):
        """Check if the API source has valid credentials"""
        params = source.get('params', {})
        for key, value in params.items():
            if key in ['key', 'token', 'api_key', 'apikey', 'access_token']:
                if not value or value.startswith('YOUR_') or value == 'PLACEHOLDER':
                    return False
        return True

    def _paginate_content(self, base_url, source, page_selector, process_func):
        """
        Fetch and process paginated content.
        
        Args:
            base_url (str): The base URL to paginate from
            source (dict): Source configuration dictionary
            page_selector (str): CSS selector to find items on each page
            process_func (callable): Function to process each found item
            
        Returns:
            tuple: (list of items found across all pages, number of pages processed)
        """
        items = []
        max_pages = source.get('max_pages', 3)
        current_page = 1
        base_url = base_url.rstrip('/')  # Remove trailing slash if present
        
        # Fetch additional pages
        while current_page < max_pages:
            current_page += 1
            
            # Add a delay between page requests
            time.sleep(2)  # 2 seconds delay
            
            next_page_url = f"{base_url}/page/{current_page}/"
            logging.info(f"Fetching page {current_page} from {next_page_url}")
            
            try:
                next_page_response = http_get(next_page_url, timeout=10, retries=2)
                
                if not next_page_response or next_page_response.status_code != 200:
                    logging.warning(f"Failed to fetch page {current_page}")
                    break
                    
                next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')
                next_page_articles = next_page_soup.find_all(page_selector)
                
                logging.info(f"Found {len(next_page_articles)} articles on page {current_page}")                    # Process articles from this page
                for idx, item in enumerate(next_page_articles):
                    if idx > 0:
                        time.sleep(1)  # 1 second delay between items
                        
                    processed_item = process_func(item, idx, current_page)
                    if processed_item:
                        items.append(processed_item)
                        
            except Exception as e:
                logging.warning(f"Error processing page {current_page}: {e}")
                break
                
        # Return both the items and the number of pages processed
        return items, current_page
    
    def _fetch_from_website(self, source):
        """Fetch data from a website source
        
        Handles specific parsing for Neuroscience News with pagination support,
        with a fallback to generic article parsing for other websites.
        
        Args:
            source: Source configuration dictionary
            
        Returns:
            list: List of article items extracted from the website
        """
        url = source['url']
        monitor = get_monitor()
        
        # Function for website fetching
        def fetch_website_content():
            # Use retry-enabled HTTP client
            response = http_get(url, timeout=10, retries=3)
            if not response or response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Custom parser for Neuroscience News (articles on topic page or homepage)
            if "neurosciencenews.com" in url:
                # First, try to get articles from the current page
                articles = soup.find_all("div", class_="meta")
                items = []
                
                # Process articles from the current page
                logging.info(f"Found {len(articles)} articles on page 1")
                for idx, meta in enumerate(articles):
                    # Add a small delay between article requests for pages after the first one
                    if idx > 0:
                        time.sleep(1)  # 1 second delay between article detail requests
                        
                    article_item = self._process_article(meta, source, idx)
                    if article_item:
                        items.append(article_item)
                
                # Fetch additional pages using the pagination helper method
                base_url = url.rstrip('/')  # Remove trailing slash if present
                
                # Define a processor function to handle each article item
                def process_article_wrapper(meta, idx, page):
                    # page parameter is available but unused 
                    return self._process_article(meta, source, idx)
                
                # Get additional items from paginated pages
                additional_items, pages_processed = self._paginate_content(
                    base_url=base_url,
                    source=source,
                    page_selector="div.meta",
                    process_func=process_article_wrapper
                )
                
                # Add additional items to our results
                items.extend(additional_items)
                
                logging.info(f"Found {len(items)} articles from Neuroscience News ({pages_processed} pages processed)")
                return items
            else:
                # Fallback: generic article parser
                articles = soup.find_all('article')
                items = []
                for art in articles:
                    title_tag = art.find(['h1', 'h2', 'h3', 'a'])
                    title = title_tag.get_text(strip=True) if title_tag else None
                    href = title_tag['href'] if title_tag and title_tag.has_attr('href') else ''
                    link = make_url_absolute(href, url) if href else url
                    desc = art.find('p').get_text(strip=True) if art.find('p') else ''
                    items.append({'title': title, 'url': link, 'description': desc})
                return items
                
        # Call the fetching function safely
        return safely_execute(
            fetch_website_content,
            error_type=f"website fetch for {url}",
            default_return=[]
        )

    def _fetch_from_api(self, source):
        """Fetch data from an API source
        
        Args:
            source: API source configuration with URL and parameters
            
        Returns:
            list: Normalized list of items from the API response
        """
        url = source['url']
        params = source.get('params', {})
        monitor = get_monitor()
        
        # Function to safely parse JSON
        def parse_json(response):
            return response.json()
            
        # Get the API response
        response = http_get(url, params=params, timeout=10, retries=3)
        if not response:
            handle_error(f"No response from API: {url}", "API fetch")
            return []
            
        if response.status_code != 200:
            handle_error(f"API returned error status: {response.status_code}", "API fetch")
            return []
            
        # Parse JSON safely
        data = safely_execute(
            parse_json, 
            args=(response,),
            error_type=f"JSON parsing for {url}", 
            default_return={}
        )
        
        # Extract and normalize data
        if 'data' in data:
            items = data['data']
        elif 'items' in data:
            items = data['items']
        elif 'results' in data:
            items = data['results']
        else:
            items = data if isinstance(data, list) else []
            
        if not items:
            logging.info(f"No items found in API response from {url}")
            
        # Normalize each item
        normalized = []
        for item in items:
            normalized_item = self._normalize_api_item(item, source)
            if normalized_item:
                normalized.append(normalized_item)
                
        logging.info(f"Normalized {len(normalized)} items from API: {url}")
        return normalized
            
    def _normalize_api_item(self, item, source):
        """Normalize an API item to a standard format
        
        Args:
            item: Raw API item
            source: Source configuration
            
        Returns:
            dict: Normalized item or None if invalid
        """
        # Skip items without title or URL
        title = item.get('title') or item.get('name')
        url_val = item.get('url') or item.get('link') or item.get('permalink')
        
        if not title or not url_val:
            return None
            
        # Build normalized item
        normalized = {
            'title': title,
            'url': url_val,
            'description': item.get('description') or item.get('summary') or item.get('content') or '',
            'date': item.get('date') or item.get('published_date') or item.get('created_at'),
            'author': item.get('author') or item.get('creator'),
            'source': source.get('name'),
            'category': source.get('category')
        }
        
        return normalized
    
    def _extract_description(self, meta, title):
        """Helper function to extract description from article metadata
        
        Args:
            meta: BeautifulSoup object for the article metadata
            title: Article title for logging
            
        Returns:
            str: Extracted description or empty string if not found
        """
        desc = ""
        
        # Method 1: Check for div with both excerpt and body-color classes
        excerpt = meta.find("div", class_=lambda c: c and "excerpt" in c and "body-color" in c)
        if excerpt:
            # Remove the "Read More" link if present
            read_more = excerpt.find("div", class_="read-more-wrap")
            if read_more:
                read_more.extract()
            
            desc = excerpt.get_text(strip=True)
            if desc:
                logging.debug(f"Found description using excerpt body-color class for '{title}'")
        
        # Method 2: Check for any div with excerpt class if method 1 failed
        if not desc:
            alt_excerpt = meta.find("div", class_=lambda c: c and "excerpt" in c)
            if alt_excerpt and alt_excerpt != excerpt:  # Don't process the same element twice
                # Remove the "Read More" link if present
                read_more = alt_excerpt.find("div", class_="read-more-wrap")
                if read_more:
                    read_more.extract()
                
                desc = alt_excerpt.get_text(strip=True)
                if desc:
                    logging.debug(f"Found description using excerpt class for '{title}'")
        
        # Method 3: Look for any paragraph in the meta area
        if not desc:
            p_tag = meta.find("p")
            if p_tag:
                desc = p_tag.get_text(strip=True)
                if desc:
                    logging.debug(f"Found description using p tag for '{title}'")
        
        return desc
        
    def _process_article(self, meta, source, idx=0):
        """Process a single article from either the main page or paginated results
        
        Args:
            meta: BeautifulSoup object for the article metadata
            source: Source configuration
            idx: Index of article for rate limiting (optional)
            
        Returns:
            dict: Dictionary with all article details or None if invalid article
        """
        # Extract title and link
        title_tag = meta.find("h3", class_="title")
        a = title_tag.find("a") if title_tag else None
        if not (a and a.text and a.get("href")):
            return None
            
        title = a.text.strip()
        # Use utility function to normalize URL
        link = make_url_absolute(a["href"], source.get("url", ""))
        
        # Extract description from listing page
        desc = self._extract_description(meta, title)
        if not desc:
            logging.warning(f"No description found for article '{title}'")
            
        # Extract image URL
        image_url = None
        mask = meta.find_previous_sibling("div", class_="mask")
        if mask:
            img = mask.find("img")
            if img and img.get("src"):
                image_url = img["src"]
                
        # Initialize metadata fields
        metadata = {
            "author": None,
            "date": None,
            "source_label": None,
            "original_research": None,
            "original_research_title": None,
            "original_research_url": None,
            "contact": None
        }
        
        try:
            # Use our retry-enabled HTTP client for article details
            art_resp = http_get(link, timeout=10)
            if art_resp and art_resp.status_code == 200:
                art_soup = BeautifulSoup(art_resp.content, 'html.parser')
                
                # Extract all metadata from article page
                article_metadata = self._extract_article_metadata(art_soup, title, link)
                
                # If we didn't find a description earlier, use the one from the article
                if not desc and article_metadata.get("description"):
                    desc = article_metadata.get("description")
                
                # Update all metadata fields
                metadata.update(article_metadata)
                
        except Exception as e:
            logging.warning(f"Failed to fetch article details for {link}: {e}")
            
        # Create the article item with all collected data
        return {
            "title": title,
            "url": link,
            "description": desc,
            "author": metadata.get("author"),
            "date": metadata.get("date"),
            "source_label": metadata.get("source_label"),
            "original_research": metadata.get("original_research"),
            "original_research_title": metadata.get("original_research_title"),
            "original_research_url": metadata.get("original_research_url"),
            "image_url": image_url,
            "contact": metadata.get("contact"),
            "source": source.get('name', 'Neuroscience News'),
            "category": source.get('category', 'news')
        }
        
    def _extract_article_metadata(self, soup, title, article_url=None):
        """Extract metadata (author, date, source, research info) from article page
        
        Args:
            soup: BeautifulSoup object for the article page
            title: Article title for logging
            article_url: URL of the article for resolving relative links
            
        Returns:
            dict: Dictionary containing metadata fields
        """
        metadata = {
            "author": None,
            "date": None,
            "source_label": None,
            "original_research": None,
            "original_research_title": None,
            "original_research_url": None,
            "contact": None,
            "description": None,
        }
        
        try:
            # Extract description/summary from article content
            entry_content = soup.find("div", class_="entry-content")
            if entry_content:
                # First look for paragraphs that start with "Summary:"
                for p in entry_content.find_all("p"):
                    p_text = p.get_text(strip=True)
                    if p_text.startswith("Summary:") or p.find("strong", text="Summary:"):
                        desc = p_text
                        if desc.startswith("Summary:"):
                            desc = desc[len("Summary:"):].strip()
                        metadata["description"] = desc
                        logging.debug(f"Found summary in article content for '{title}'")
                        break
                
                # If still no description, get the first paragraph of content as fallback
                if not metadata["description"] and entry_content.find("p"):
                    first_p = entry_content.find("p")
                    if first_p and first_p.get_text(strip=True):
                        metadata["description"] = first_p.get_text(strip=True)
                        logging.debug(f"Using first paragraph as description for '{title}'")
                        
            # Look for metadata in has-background paragraphs
            for p in soup.find_all("p", class_="has-background"):
                strongs = p.find_all("strong")
                for strong in strongs:
                    label = strong.text.strip()
                    if label.startswith("Author:"):
                        author_link = strong.find_next_sibling("a")
                        if author_link and author_link.text:
                            metadata["author"] = author_link.text.strip()
                        else:
                            metadata["author"] = strong.next_sibling.strip() if strong.next_sibling else None
                    elif label.startswith("Source:"):
                        source_link = strong.find_next_sibling("a")
                        if source_link and source_link.text:
                            metadata["source_label"] = source_link.text.strip()
                        else:
                            metadata["source_label"] = strong.next_sibling.strip() if strong.next_sibling else None
                    elif label.startswith("Contact:"):
                        metadata["contact"] = strong.next_sibling.strip() if strong.next_sibling else None
                    elif label.startswith("Image:"):
                        pass  # Skip image processing
                    elif label.startswith("Original Research:"):
                        metadata.update(self._extract_research_info(strong, article_url))
                        
            # Extract the date
            time_tag = soup.find("time", class_="entry-date published dateCreated flipboard-date")
            if time_tag and time_tag.get("datetime"):
                metadata["date"] = time_tag["datetime"]
            elif time_tag:
                metadata["date"] = time_tag.get_text(strip=True)
                
        except Exception as e:
            logging.warning(f"Error extracting article metadata: {e}")
            
        return metadata
        
    def _extract_research_info(self, strong_tag, article_url=None):
        """Extract research information from a strong tag
        
        Args:
            strong_tag: BeautifulSoup strong tag containing "Original Research:" text
            article_url (str, optional): Article URL for resolving relative links
            
        Returns:
            dict: Dictionary with research information
        """
        result = {
            "original_research": None,
            "original_research_title": None,
            "original_research_url": None
        }
        
        try:
            orig_link = strong_tag.find_next_sibling("a")
            if orig_link and orig_link.text and orig_link.get("href"):
                result["original_research_title"] = orig_link.text.strip()
                result["original_research"] = f"Research: {result['original_research_title']}"
                result["original_research_url"] = make_url_absolute(orig_link["href"].strip(), article_url)
                logging.debug(f"Found research with direct URL: '{result['original_research_title']}' -> {result['original_research_url']}")
            elif orig_link and orig_link.text:
                result["original_research_title"] = orig_link.text.strip()
                result["original_research"] = f"Research: {result['original_research_title']}"
                
                # Try to find the URL in a parent element if not in the immediate link
                parent_a = orig_link.find_parent("a")
                if parent_a and parent_a.get("href"):
                    result["original_research_url"] = make_url_absolute(parent_a["href"].strip(), article_url)
                    logging.debug(f"Found research with parent URL: '{result['original_research_title']}' -> {result['original_research_url']}")
                else:
                    # Try to find a nearby link that might contain the URL
                    next_a = orig_link.find_next_sibling("a")
                    if next_a and next_a.get("href"):
                        result["original_research_url"] = make_url_absolute(next_a["href"].strip(), article_url)
                        logging.debug(f"Found research with sibling URL: '{result['original_research_title']}' -> {result['original_research_url']}")
                    else:
                        logging.debug(f"Found research WITHOUT URL: '{result['original_research_title']}'")
            else:
                # Get the text after "Original Research:" but use "Research:" in our data structure
                raw_text = strong_tag.next_sibling.strip() if strong_tag.next_sibling else None
                if raw_text:
                    # Replace "Original Research:" prefix if it exists in the text
                    if raw_text.startswith("Original Research:"):
                        result["original_research"] = "Research:" + raw_text[len("Original Research:"):]
                    else:
                        result["original_research"] = "Research: " + raw_text
        except Exception as e:
            logging.warning(f"Error extracting research info: {e}")
            
        return result