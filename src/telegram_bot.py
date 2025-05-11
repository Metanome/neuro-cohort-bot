from telegram import Bot
from telegram.error import TelegramError
import logging

class TelegramBot:
    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    def send_message(self, message):
        try:
            self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode='Markdown')
            logging.info("Message sent to Telegram group.")
        except TelegramError as e:
            logging.error(f"Failed to send message: {e}")