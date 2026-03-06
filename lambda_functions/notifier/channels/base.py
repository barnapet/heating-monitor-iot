import json
import logging
import urllib.request
import urllib.error
from abc import ABC, abstractmethod

logging.getLogger(__name__)

class NotificationChannel(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass
    
    def _make_http_post(self, url: str, payload: dict, headers: dict = None) -> None:
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if not (200 <= response.getcode() < 300):
                    raise urllib.error.URLError(f"HTTP Error: {response.getcode()}")
                
        except urllib.error.URLError as e:
            logger.error(f"Network error when calling {url} : {e}")
            raise 