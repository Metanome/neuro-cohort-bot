# Neuro Cohort Bot

Neuro Cohort is a Python-based Telegram bot designed to aggregate and post updates related to Neuroscience. The bot periodically scrapes or fetches data from various sources, cleans and categorizes the data, and posts updates to a designated Telegram group.

## Features

- **Data Aggregation**: Collects updates from multiple sources including news articles, events, job postings, videos, and interesting facts.
- **Data Cleaning**: Removes duplicates and irrelevant entries to ensure high-quality content.
- **Categorization**: Organizes data into predefined categories for better clarity.
- **Telegram Integration**: Sends formatted messages to a specified group topic on Telegram.
- **Logging**: Logs all events, warnings, and errors to a rotating log file for later review.
- **Scheduled Runs**: Uses APScheduler to automate data collection and posting.

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
└── main.py
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/neuro-cohort-bot.git
   cd neuro-cohort-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your data sources in `config/sources.yaml`.

## Usage

To run the bot, execute the following command:
```
python main.py
```

The bot will start collecting data from the configured sources and posting updates to the specified Telegram group.

## Logging

Logs are stored in the `logs` directory. The logging configuration is set to rotate logs at 10MB, keeping 5 backups. 

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.