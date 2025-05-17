"""
Telegram Bot wrapper for the Neuro Cohort Bot.

This module provides an asynchronous wrapper around python-telegram-bot
to handle message sending to Telegram channels or groups, with support
for group topics and error handling for rate limits.
"""
import re
import logging
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from src.utils import handle_error

class TelegramBot:
    def __init__(self, token, chat_id, topic_id=None):
        self.bot = Bot(token=token)  # Telegram Bot instance
        self.chat_id = chat_id  # Group or channel ID
        self.topic_id = topic_id  # message_thread_id for topics

    # Send a message to the Telegram group/topic (async for python-telegram-bot v20+)
    async def send_message(self, message):
        try:
            kwargs = dict(
                chat_id=self.chat_id, 
                text=message, 
                parse_mode='MarkdownV2',  # Use MarkdownV2 for formatting
                disable_web_page_preview=True  # Disable link previews
            )
            if self.topic_id:
                kwargs['message_thread_id'] = int(self.topic_id)  # Support group topics
            await self.bot.send_message(**kwargs)  # Send the message
            logging.info("Message sent to Telegram group.")
        except TelegramError as e:
            # Check if rate limited
            if "retry after" in str(e).lower():
                retry_time = self._extract_retry_time(str(e))
                logging.warning(f"Telegram rate limit hit. Retrying after {retry_time} seconds.")
                await asyncio.sleep(retry_time + 1)  # Wait a bit longer than requested
                # Recursive retry after waiting
                return await self.send_message(message)
            handle_error(e, "telegram_api", with_traceback=True)  # Log Telegram API errors
        except Exception as e:
            handle_error(e, "telegram_unexpected", with_traceback=True)  # Log unexpected errors
    
    def _extract_retry_time(self, error_message):
        """Extract retry time from Telegram error message"""
        match = re.search(r"retry after (\d+)", error_message, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 30  # Default retry delay if we can't parse it