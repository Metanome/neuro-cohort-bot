class DataFetcher:
    def __init__(self, sources):
        self.sources = sources

    def fetch_data(self):
        all_data = []
        for source in self.sources:
            if source['type'] == 'website':
                data = self._fetch_from_website(source)
            elif source['type'] == 'api':
                data = self._fetch_from_api(source)
            else:
                data = []
            # Add category and source name to each item
            for item in data:
                item['category'] = source.get('category')
                item['source'] = source.get('name')
            all_data.extend(data)
        return all_data

    def _fetch_from_website(self, source):
        from bs4 import BeautifulSoup
        import requests
        url = source['url']
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Example: extract articles with <article> tags
                articles = soup.find_all('article')
                items = []
                for art in articles:
                    title_tag = art.find(['h1', 'h2', 'h3', 'a'])
                    title = title_tag.get_text(strip=True) if title_tag else None
                    link = title_tag['href'] if title_tag and title_tag.has_attr('href') else url
                    desc = art.find('p').get_text(strip=True) if art.find('p') else ''
                    items.append({'title': title, 'url': link, 'description': desc})
                return items
            else:
                return []
        except Exception as e:
            import logging
            logging.warning(f"Website fetch failed for {url}: {e}")
            return []

    def _fetch_from_api(self, source):
        import requests
        url = source['url']
        params = source.get('params', {})
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Example: flatten and normalize API data
                if 'data' in data:
                    items = data['data']
                elif 'items' in data:
                    items = data['items']
                else:
                    items = data if isinstance(data, list) else []
                # Normalize each item
                normalized = []
                for item in items:
                    title = item.get('title') or item.get('name') or 'No Title'
                    url_val = item.get('url') or item.get('link') or ''
                    desc = item.get('description') or item.get('summary') or ''
                    normalized.append({'title': title, 'url': url_val, 'description': desc})
                return normalized
            else:
                return []
        except Exception as e:
            import logging
            logging.warning(f"API fetch failed for {url}: {e}")
            return []