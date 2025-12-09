import json
import logging
import urllib.request
import urllib.error
from .base import NotificationChannel

logger = logging.getLogger()

class TelegramNotifier(NotificationChannel):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def send(self, message: str) -> bool:
        if not self.token or not self.chat_id:
            logger.warning("Telegram config missing (token or chat_id).")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    logger.info("Telegram message sent successfully.")
                    return True
        except urllib.error.URLError as e:
            logger.error(f"Telegram error: {e}")
        
        return False