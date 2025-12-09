import json
import logging
import os
import boto3
from channels.telegram import TelegramNotifier
from channels.discord import DiscordNotifier

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')

def get_secret(env_var_key):
    path = os.environ.get(env_var_key)
    if not path:
        return None
        
    try:
        response = ssm.get_parameter(Name=path, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Failed to fetch secret for {env_var_key} (path: {path}): {e}")
        return None

def get_active_channels():
    channels = []

    token = get_secret('SSM_KEY_TOKEN')
    chat_id = get_secret('SSM_KEY_CHAT_ID')
    discord_url = get_secret('SSM_KEY_DISCORD_WEBHOOK')

    if token and chat_id:
        channels.append(TelegramNotifier(token=token, chat_id=chat_id))
    else:
        logger.warning("Telegram secrets missing from SSM.")

    if discord_url and discord_url.startswith("https"):
        channels.append(DiscordNotifier(webhook_url=discord_url))
    else:
        logger.warning("Discord URL missing or invalid in SSM.")

    return channels

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    
    status = event.get('status', 'UNKNOWN')
    device_id = event.get('device_id', 'n/a')
    
    if status == 'INACTIVE':
        message = f" <b>ALERT</b> \nThe boiler is inactive!\nDevice: <code>{device_id}</code>"
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