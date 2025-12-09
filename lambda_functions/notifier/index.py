import json
import logging
from channels.telegram import TelegramNotifier
from channels.discord import DiscordNotifier

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_active_channels():
    """Aggregates the available (configured) notification channels."""
    channels = []
    
    tg = TelegramNotifier()
    if tg.token and tg.chat_id:
        channels.append(tg)
    
    dc = DiscordNotifier()
    
    raw_url = dc.webhook_url
    logger.info(f"DEBUG: Discord Webhook check. Value: '{str(raw_url)[:15]}...'")

    if dc.webhook_url and dc.webhook_url.startswith("https"):
        logger.info("DEBUG: Discord URL appears valid, channel ADDED.")
        channels.append(dc)
    else:
        logger.warning("DEBUG: Discord URL missing or invalid! (Skipping).")
        
    return channels

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    
    status = event.get('status', 'UNKNOWN')
    device_id = event.get('device_id', 'n/a')
    
    if status == 'INACTIVE':
        message = f"⚠️ <b>ALERT</b> ⚠️\nThe boiler is inactive!\nDevice: <code>{device_id}</code>"
    else:
        message = f"Status info: {status} (Device: {device_id})"

    active_channels = get_active_channels()
    
    if not active_channels:
        logger.error("No notification channels configured!")
        return {
            "statusCode": 500, 
            "body": json.dumps("No notification channels configured")
        }

    success_count = 0
    for channel in active_channels:
        try:
            if channel.send(message):
                success_count += 1
        except Exception as e:
            logger.error(f"ERROR sending to {type(channel).__name__}: {e}")

    result_msg = f"Message sent to {success_count}/{len(active_channels)} channels."
    logger.info(result_msg)

    return {
        "statusCode": 200,
        "body": json.dumps(result_msg)
    }
```