import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Async scheduler for periodic jobs
from src.config_loader import load_config  # Loads YAML config for sources and Telegram
from src.data_fetcher import DataFetcher  # Fetches data from all sources
from src.data_cleaner import clean_data  # Deduplicates and filters data
from src.categorizer import categorize_data  # Categorizes data into news, events, etc.
from src.message_formatter import format_message, save_posted_url  # Formats messages for Telegram, tracks posted URLs
from src.telegram_bot import TelegramBot  # Async Telegram bot wrapper
from src.logger_setup import setup_logger  # Rotating file logger setup
from src.status_monitor import get_monitor, send_status_report  # Status monitoring
from src.utils import cleanup_old_logs, handle_error  # Common utility functions


# Helper functions for data processing pipeline
def update_source_statistics(data_items, source_configs):
    """
    Update statistics for each data source based on fetched items.
    
    Args:
        data_items (list): Raw data items fetched from all sources
        source_configs (list): Source configuration entries from config file
        
    Returns:
        dict: Status for each source (name -> status message)
    """
    # Count items per source
    source_count = {}
    for item in data_items:
        source_name = item.get('source', 'Unknown')
        if source_name in source_count:
            source_count[source_name] += 1
        else:
            source_count[source_name] = 1
    
    # Create status dictionary
    source_statuses = {}
    for source in source_configs:
        source_name = source.get('name', 'Unknown')
        count = source_count.get(source_name, 0)
        source_statuses[source_name] = f"OK ({count} items)" if count > 0 else "No data"
        
    return source_statuses


async def send_messages_to_telegram(messages, telegram_bot, message_delay=3, monitor=None):
    """
    Send formatted messages to Telegram with rate limiting.
    
    Args:
        messages (list): List of (message_text, url) tuples to send
        telegram_bot (TelegramBot): Telegram bot instance
        message_delay (int): Delay in seconds between messages
        monitor (StatusMonitor, optional): Status monitor for error tracking
        
    Returns:
        int: Number of messages successfully sent
    """
    post_count = 0
    
    for msg, url in messages:
        try:
            # Send the message
            await telegram_bot.send_message(msg)
            
            # Record the URL as posted
            save_posted_url(url)
            post_count += 1
            
            # Add delay between messages to prevent rate limiting
            if post_count < len(messages):  # Don't delay after the last message
                logging.debug(f"Waiting {message_delay} seconds before sending next message...")
                await asyncio.sleep(message_delay)
                
        except Exception as e:
            error_msg = handle_error(e, "telegram_message_send", with_traceback=True)
            
            # Record error if monitor is available
            if monitor:
                monitor.record_error("telegram", error_msg)
    
    return post_count


async def maybe_send_status_report(run_id, telegram_bot):
    """
    Send a periodic status report to Telegram if it's time.
    
    Args:
        run_id (int): Current run ID/counter
        telegram_bot (TelegramBot): Telegram bot instance
    """
    # Send periodic status report (every 24 hours based on run count)
    # Assuming 30-minute intervals, this means once a day
    if run_id % 48 == 0:
        try:
            status_msg = send_status_report()
            await telegram_bot.send_message(status_msg)
            logging.info("Status report sent to Telegram.")
        except Exception as e:
            handle_error(e, "status_report", with_traceback=True)

# Set up the async scheduler for periodic data collection and log cleanup
def setup_async_scheduler(data_collection_function, fetcher, telegram_bot, config, log_cleanup_days=30):
    """
    Set up the asynchronous scheduler for periodic tasks.
    
    Args:
        data_collection_function (callable): Async function to collect and process data
        fetcher (DataFetcher): Data fetcher instance
        telegram_bot (TelegramBot): Telegram bot instance
        config (dict): Application configuration
        log_cleanup_days (int): Number of days to keep log files
        
    Returns:
        AsyncIOScheduler: Configured and started scheduler
    """
    # Get interval from config or use default (30 minutes)
    run_interval = config.get('settings', {}).get('run_interval_minutes', 30)
    
    # Create a new AsyncIO-based scheduler
    scheduler = AsyncIOScheduler()
    
    # Add the main data collection job
    scheduler.add_job(
        data_collection_function,
        'interval',
        minutes=run_interval,
        id='data_collection_job',
        args=[config, fetcher, telegram_bot]
    )
    logging.info(f'Scheduler set up to run every {run_interval} minute(s) at {datetime.now()}')
    
    # Schedule log cleanup daily at midnight
    scheduler.add_job(
        lambda: cleanup_old_logs('logs', log_cleanup_days),
        'cron',
        hour=0,
        minute=0,
        id='log_cleanup_job'
    )
    
    # Start the scheduler
    scheduler.start()
    return scheduler

# The main data collection and posting pipeline
async def data_collection_pipeline(config, fetcher, telegram_bot):
    """
    Main data collection and processing pipeline that runs periodically.
    
    This function fetches data from all sources, processes it, and sends new content
    to the Telegram channel.
    
    Args:
        config (dict): Application configuration
        fetcher (DataFetcher): Data fetcher instance
        telegram_bot (TelegramBot): Telegram bot instance
    """
    # Get status monitor
    monitor = get_monitor()
    run_id = monitor.record_run_start()
    
    source_statuses = {}
    post_count = 0
    success = True
    
    try:
        logging.info(f"Starting data collection pipeline (Run #{run_id})...")
        
        # Step 1: Fetch raw data from all sources
        raw_data = fetcher.fetch_data()
        logging.info(f"Data fetched from {len(raw_data)} items across {len(config['sources'])} sources.")
        
        # Step 2: Track source statistics for monitoring
        source_statuses = update_source_statistics(raw_data, config['sources'])
        
        # Step 3: Clean and categorize data
        cleaned_data = clean_data(raw_data)
        logging.info(f"Data cleaned: {len(cleaned_data)} of {len(raw_data)} items kept after deduplication.")
        
        categorized_data = categorize_data(cleaned_data)
        logging.info("Data categorized by type.")
        
        # Step 4: Format messages for Telegram
        messages = format_message(categorized_data)
        logging.info(f"Messages formatted for Telegram: {len(messages)} new messages.")
        
        # Step 5: Send messages
        if messages:
            post_count = await send_messages_to_telegram(
                messages, 
                telegram_bot, 
                config.get('settings', {}).get('message_delay_seconds', 3),
                monitor
            )
            success = post_count == len(messages)  # Success if all messages were sent
            logging.info(f"{post_count} message(s) sent to Telegram group.")
        else:
            logging.info("No new content to send to Telegram group.")
        
        # Step 6: Send periodic status report (every 24 hours based on run count)
        await maybe_send_status_report(run_id, telegram_bot)
    
    except Exception as e:
        error_msg = handle_error(e, "data_collection_pipeline", with_traceback=True)
        monitor.record_error("pipeline", error_msg)
        success = False
    
    # Step 7: Record run completion for monitoring
    monitor.record_run_complete(success=success, posts=post_count, source_statuses=source_statuses)

# Main entry point for the bot
async def main():
    """
    Main entry point for the Neuro Cohort Bot application.
    
    This function initializes the logger, loads configuration,
    sets up the data fetcher and Telegram bot, and starts the
    scheduled data collection process.
    """
    setup_logger()  # Initialize rotating file logger
    logging.info("Starting Neuro Cohort Bot...")
    
    try:
        config = load_config('config/sources.yaml')  # Load config (sources, Telegram credentials)
        logging.info("Configuration loaded successfully.")
        
        # Get run interval from config or use default (30 minutes)
        run_interval = config.get('settings', {}).get('run_interval_minutes', 30)
        
        fetcher = DataFetcher(config['sources'])  # Create data fetcher
        telegram_token = config['telegram']['token']  # Telegram bot token
        telegram_chat_id = config['telegram']['chat_id']  # Telegram group/chat ID
        telegram_topic_id = config['telegram'].get('topic_id')  # Optional: group topic/thread ID
        telegram_bot = TelegramBot(telegram_token, telegram_chat_id, telegram_topic_id)  # Telegram bot instance
        
        # Run data collection pipeline once at startup
        await data_collection_pipeline(config, fetcher, telegram_bot)
        
        # Setup async scheduler for periodic runs and log cleanup
        log_retention_days = config.get('settings', {}).get('log_retention_days', 30)
        scheduler = setup_async_scheduler(data_collection_pipeline, fetcher, telegram_bot, config, log_retention_days)
        logging.info(f"Scheduler set up for periodic data collection every {run_interval} minutes")
        
        # Keep the main thread alive so the scheduler keeps running
        try:
            while True:
                await asyncio.sleep(60)  # Sleep to keep event loop alive
        except (KeyboardInterrupt, SystemExit):
            logging.info("Bot stopping due to user interrupt...")
            scheduler.shutdown()
            logging.info("Scheduler shut down gracefully.")
    except Exception as e:
        handle_error(e, "main_function", with_traceback=True)
        logging.critical("Application terminating due to fatal error.")
        raise

if __name__ == "__main__":
    asyncio.run(main())  # Start the async main function