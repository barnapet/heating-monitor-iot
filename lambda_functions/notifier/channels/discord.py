import os
import json
import logging
import urllib.request
import urllib.error
from .base import NotificationChannel

logger = logging.getLogger()

class DiscordNotifier(NotificationChannel):
    def __init__(self):
        self.webhook_url = os.environ.get('SSM_KEY_DISCORD_WEBHOOK')

    def send(self, message: str) -> bool:
        if not self.webhook_url:
            logger.warning("Discord Webhook URL missing.")
            return False

        payload = {
            "content": message,
            "username": "Boiler Monitor"
        }

        data = json.dumps(payload).encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0' 
        }
        
        req = urllib.request.Request(self.webhook_url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if 200 <= response.getcode() < 300:
                    logger.info("Discord message sent successfully.")
                    return True
        except urllib.error.URLError as e:
            logger.error(f"Discord error: {e}")
            
        return False