# Neuro Cohort Bot

Neuro Cohort is a Python-based Telegram bot designed to aggregate and post updates related to Neuroscience. The bot periodically scrapes or fetches data from various sources, cleans and categorizes the data, and posts updates to a designated Telegram group.

## Features

- **Data Aggregation:** Collects updates from multiple sources including news articles, events, job postings, videos, and interesting facts (from both websites and APIs).
- **Data Cleaning:** Removes duplicates and irrelevant entries to ensure high-quality content.
- **Categorization:** Organizes data into predefined categories: news, events, jobs, videos/courses, facts.
- **Telegram Integration:** Sends formatted messages (Markdown) to a specified group topic on Telegram.
- **Logging:** Logs all events, warnings, and errors to a rotating log file for later review. Old logs are cleaned up automatically.
- **Scheduled Runs:** Uses APScheduler to automate data collection, posting, and log cleanup.

## Project Structure

```
neuro-cohort-bot
├── src
│   ├── __init__.py
│   ├── config_loader.py
│   ├── data_fetcher.py
│   ├── data_cleaner.py
│   ├── categorizer.py
│   ├── message_formatter.py
│   ├── telegram_bot.py
│   ├── scheduler.py
│   └── logger_setup.py
├── config
│   └── sources.yaml
├── logs
│   └── (rotating log files)
├── requirements.txt
├── README.md
├── LICENSE
└── main.py
```

## Configuration

All sources and Telegram credentials are defined in `config/sources.yaml`:

```yaml
sources:
  - name: Neuroscience News
    type: website
    category: news
    url: "https://neurosciencenews.com/"
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
    url: "https://example-facts-source.com/"

telegram:
  token: "YOUR_TELEGRAM_BOT_TOKEN"
  chat_id: "YOUR_TELEGRAM_CHAT_ID"
```

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Metanome/neuro-cohort-bot.git
   cd neuro-cohort-bot
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your data sources and Telegram credentials in `config/sources.yaml`.

## Usage

To run the bot, execute:
```sh
python main.py
```
The bot will start collecting data from the configured sources and posting updates to the specified Telegram group. Data collection and posting are repeated every 30 minutes by default.

## Logging

- Logs are stored in the `logs` directory.
- Rotates at 10MB, keeps 5 backups.
- Old logs (older than 30 days) are automatically deleted.

## Customization

- To add new sources, edit `config/sources.yaml` and provide extraction rules as needed.
- To change the schedule, edit the interval in `src/scheduler.py`.
- To adjust log retention, change the `log_cleanup_days` parameter in the scheduler.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for suggestions or improvements.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](https://github.com/Metanome/neuro-cohort-bot/blob/main/LICENSE) file for details.