import logging
from src.config_loader import load_config
from src.data_fetcher import DataFetcher
from src.data_cleaner import clean_data
from src.categorizer import categorize_data
from src.message_formatter import format_message
from src.telegram_bot import TelegramBot
from src.scheduler import setup_scheduler
from src.logger_setup import setup_logger


def data_collection_pipeline(config, fetcher, telegram_bot):
    logging.info("Starting data collection pipeline...")
    # Fetch data
    raw_data = fetcher.fetch_data()
    logging.info("Data fetched from sources.")
    # Clean data
    cleaned_data = clean_data(raw_data)
    logging.info("Data cleaned.")
    # Categorize data
    categorized_data = categorize_data(cleaned_data)
    logging.info("Data categorized.")
    # Format message
    message = format_message(categorized_data)
    logging.info("Message formatted for Telegram.")
    # Send message
    telegram_bot.send_message(message)
    logging.info("Message sent to Telegram group.")


def main():
    setup_logger()
    logging.info("Starting Neuro Cohort Bot...")

    # Load configuration
    config = load_config('config/sources.yaml')
    logging.info("Configuration loaded successfully.")

    # Initialize data fetcher
    fetcher = DataFetcher(config)

    # Initialize Telegram bot (replace with your actual config structure)
    telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with actual config usage
    telegram_chat_id = "YOUR_TELEGRAM_CHAT_ID"  # Replace with actual config usage
    telegram_bot = TelegramBot(telegram_token, telegram_chat_id)

    # Run data collection pipeline once at startup
    data_collection_pipeline(config, fetcher, telegram_bot)

    # Setup scheduler for periodic runs
    setup_scheduler(lambda: data_collection_pipeline(config, fetcher, telegram_bot))
    logging.info("Scheduler set up for periodic data collection.")

if __name__ == "__main__":
    main()