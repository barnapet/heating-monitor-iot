import logging
from .base import NotificationChannel

logger = logging.getLogger(__name__)

class DiscordNotifier(NotificationChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, message: str) -> None:
        if not self.webhook_url:
            logger.error("The Discord webhook URL is missing.")
            raise ValueError("Critical Error: Missing Discord webhook URL!")

        payload = {
            "content": message,
            "username": "Boiler Monitor"
        }

        logger.info("The Discord message has started to be sent successfully.")
        self._make_http_post(self.webhook_url, payload)
        logger.info("The Discord message has been sent successfully.")