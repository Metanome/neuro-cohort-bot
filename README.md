# Neuro Cohort Bot

Neuro Cohort is a Python-based Telegram bot designed to aggregate and post updates related to Neuroscience. The bot periodically scrapes or fetches data from various sources, cleans and categorizes the data, and posts updates to a designated Telegram group. It uses asynchronous processing for improved performance and reliability.

## Table of Contents
- [Neuro Cohort Bot](#neuro-cohort-bot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Running in Background](#running-in-background)
    - [Operation](#operation)
  - [Logging](#logging)
  - [Customization](#customization)
    - [Adding New Sources](#adding-new-sources)
    - [Adjusting Bot Behavior](#adjusting-bot-behavior)
  - [Module Overview](#module-overview)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Data Aggregation:** Collects updates from multiple sources including news articles, events, job postings, videos, and interesting facts (from both websites and APIs).
- **Pagination Support:** Fetches multiple pages from sources to ensure comprehensive content retrieval, with configurable page limits.
- **Article Summaries:** Automatically extracts and includes descriptions/summaries of articles for better context.
- **Data Cleaning:** Removes duplicates and irrelevant entries to ensure high-quality content.
- **Categorization:** Organizes data into predefined categories: news, events, jobs, videos/courses, facts.
- **Telegram Integration:** Sends formatted messages (Markdown) to a specified group topic on Telegram.
- **Article Details:** Includes comprehensive metadata such as author, date, source, and research links.
- **Anti-Rate Limiting:** Adds configurable delays between messages to prevent Telegram rate limiting.
- **Automatic Retries:** Automatically handles rate limiting by waiting and retrying when necessary.
- **Status Reports:** Sends periodic status reports to Telegram to track bot health and performance.
- **Logging:** Logs all events, warnings, and errors to a rotating log file for later review. Old logs are cleaned up automatically.
- **Scheduled Runs:** Uses APScheduler to automate data collection, posting, and log cleanup.
- **Asynchronous Processing:** Leverages Python's asyncio for non-blocking operations and improved concurrency.

## Project Structure

```
neuro-cohort-bot
├── src
│   ├── __init__.py
│   ├── categorizer.py
│   ├── config_loader.py
│   ├── data_cleaner.py
│   ├── data_fetcher.py
│   ├── http_utils.py
│   ├── logger_setup.py
│   ├── message_formatter.py
│   ├── pagination_utils.py
│   ├── status_monitor.py
│   ├── telegram_bot.py
│   └── utils.py
├── config
│   └── sources.yaml
├── logs
│   └── (rotating log files)
├── requirements.txt
├── README.md
├── LICENSE
├── main.py
└── status.json
```

## Configuration

All settings, sources, and Telegram credentials are defined in `config/sources.yaml`:

```yaml
# Global settings
settings:
  run_interval_minutes: 30    # How often to run the data collection pipeline
  log_retention_days: 30      # How many days to keep log files
  url_retention_days: 90      # How many days to remember posted URLs
  max_stored_urls: 5000       # Maximum number of URLs to store in history
  status_report_hours: 24     # How often to send status reports
  message_delay_seconds: 3    # Delay between messages to prevent rate limiting

sources:
  - name: Neuroscience News
    type: website
    category: news
    url: "https://neurosciencenews.com/neuroscience-topics/neuroscience/"
    max_pages: 3              # Fetch up to 3 pages of content
  - name: Eventbrite Neuroscience Events
    type: api
    category: events
    url: "https://www.eventbriteapi.com/v3/events/search/"
    params:
      token: "YOUR_EVENTBRITE_API_TOKEN"
  - name: YouTube Neuroscience Videos
    type: api
    category: videos/courses
    url: "https://www.googleapis.com/youtube/v3/search"
    params:
      key: "YOUR_YOUTUBE_API_KEY"
      q: "neuroscience videos"
  - name: Neuroscience Fun Facts
    type: website
    category: facts
    url: "https://www.brainfacts.org/"

telegram:
  token: "YOUR_TELEGRAM_BOT_TOKEN"
  chat_id: "YOUR_TELEGRAM_CHAT_ID"
  topic_id: "YOUR_TELEGRAM_TOPIC_ID"
```

## Requirements

- Python 3.7 or higher
- Required packages (see `requirements.txt`):
  - python-telegram-bot
  - beautifulsoup4
  - requests
  - pyyaml
  - apscheduler
  - urllib3

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Metanome/neuro-cohort-bot.git
   cd neuro-cohort-bot
   ```

2. Create and activate a virtual environment:
   ```sh
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Configuration setup:
   - Copy `config/sources.yaml.example` to `config/sources.yaml` (if provided)
   - Edit `config/sources.yaml` with your Telegram API credentials and desired sources
   - Obtain a Telegram bot token from [@BotFather](https://t.me/botfather)
   - Find your Telegram chat ID using [@userinfobot](https://t.me/userinfobot)

## Usage

### Basic Usage

To run the bot in the foreground:
```sh
python main.py
```

### Running in Background

For Windows users:
```sh
start /B python main.py > bot_output.log 2>&1
```

For Linux/Mac users:
```sh
nohup python main.py > bot_output.log 2>&1 &
```

### Operation

Once started, the bot will:
1. Load configurations from the YAML file
2. Fetch data from all configured sources
3. Clean and categorize the collected data
4. Format and send new items to the Telegram group
5. Repeat this process every 30 minutes (configurable)

All operations are logged to the `logs` directory for monitoring.

## Logging

The application uses a comprehensive logging system:

- **Location**: All logs are stored in the `logs` directory
- **Rotation**: Log files rotate at 10MB with 5 backups maintained
- **Cleanup**: Old logs (older than 30 days) are automatically deleted
- **Levels**: Different log levels (DEBUG, INFO, WARNING, ERROR) are used for appropriate messages
- **Format**: Each log entry includes timestamp, level, and contextual information

## Customization

### Adding New Sources

To add new data sources:
1. Edit `config/sources.yaml`
2. Add a new entry under the `sources` section
3. Specify `name`, `type`, `category`, and `url` at minimum
4. For API sources, add required parameters in the `params` section

### Adjusting Bot Behavior

- **Schedule**: Modify `run_interval_minutes` in the `settings` section
- **Log Retention**: Change `log_retention_days` in the `settings` section
- **URL History**: Adjust `url_retention_days` and `max_stored_urls` to manage URL history
- **Telegram Rate Limiting**: Set `message_delay_seconds` (3-5 seconds recommended for larger groups)
- **Status Reports**: Configure `status_report_hours` to change reporting frequency

## Module Overview

- **main.py**: Entry point and orchestration of all bot operations
- **src/categorizer.py**: Categorizes content into different types (news, events, jobs, etc.)
- **src/config_loader.py**: Loads and validates YAML configuration from files
- **src/data_cleaner.py**: Removes duplicates and cleans up data
- **src/data_fetcher.py**: Retrieves data from various configured sources
- **src/http_utils.py**: Handles HTTP requests with retry logic
- **src/logger_setup.py**: Sets up rotating file logging
- **src/message_formatter.py**: Formats data into Telegram-compatible messages
- **src/pagination_utils.py**: Manages pagination for multi-page content
- **src/status_monitor.py**: Tracks application health and performance
- **src/telegram_bot.py**: Handles communication with the Telegram API
- **src/utils.py**: Common utility functions used across modules

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for suggestions or improvements.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](https://github.com/Metanome/neuro-cohort-bot/blob/main/LICENSE) file for details.