import logging
from .base import NotificationChannel

logger = logging.getLogger(__name__)

class TelegramNotifier(NotificationChannel):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def send(self, message: str) -> None:
        if not self.token or not self.chat_id:
            logger.error("Telegram config missing (token or chat_id).")
            raise ValueError("Critical Error: Missing Telegram token or missing Chat ID!")

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        logger.info("The Telegram message has started to be sent successfully.")
        self._make_http_post(url, payload)
        logger.info("The Telegram message has been sent successfully.")
        
        