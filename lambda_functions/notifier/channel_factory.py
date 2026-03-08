import os
import logging
import boto3
from channels.telegram import TelegramNotifier
from channels.discord import DiscordNotifier

logger = logging.getLogger(__name__)

ssm = boto3.client('ssm')

CHANNEL_REGISTRY = {
    TelegramNotifier: {
        'token': 'SSM_KEY_TOKEN',
        'chat_id': 'SSM_KEY_CHAT_ID'
    },
    DiscordNotifier: {
        'webhook_url': 'SSM_KEY_DISCORD_WEBHOOK'
    }
}

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
    """Returns a list of successfully configured notification channels."""
    channels = []

    for notifier_class, secret_mapping in CHANNEL_REGISTRY.items():
        kwargs = {}
        for param_name, ssm_key in secret_mapping.items():
            secret_value = get_secret(ssm_key)
            if secret_value and (param_name != 'webhook_url' or secret_value.startswith('https')):
                kwargs[param_name] = secret_value
        
        if len(kwargs) == len(secret_mapping):
            channels.append(notifier_class(**kwargs))
            logger.info(f"Successfully configured: {notifier_class.__name__}")
        else:
            logger.warning(f"Missing secrets for {notifier_class.__name__}. Skipping.")

    return channels