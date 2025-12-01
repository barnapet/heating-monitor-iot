import json
import os
import datetime
import logging
import urllib3
import boto3
from botocore.exceptions import ClientError

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients outside the handler for connection reuse (optimization)
ssm = boto3.client('ssm')
http = urllib3.PoolManager()

def get_secret(parameter_name, is_secure=False):
    """
    Retrieves a parameter from AWS Systems Manager Parameter Store.
    """
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=is_secure)
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Failed to fetch parameter {parameter_name}: {e}")
        raise e

def lambda_handler(event, context):
    """
    Main handler for the Hot Path.
    Triggered by IoT Rule when status='INACTIVE'.
    Sends an alert to Telegram.
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # 1. Retrieve Secrets (Runtime)
    try:
        # Get parameter names from environment variables
        token_param_name = os.environ.get('SSM_KEY_TOKEN')
        chat_id_param_name = os.environ.get('SSM_KEY_CHAT_ID')

        if not token_param_name or not chat_id_param_name:
            raise ValueError("Missing SSM parameter names in environment variables.")

        # Fetch actual values from SSM
        telegram_token = get_secret(token_param_name, is_secure=True)
        telegram_chat_id = get_secret(chat_id_param_name, is_secure=False)
        
        telegram_api_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise RuntimeError("Failed to load configuration from SSM.")

    # 2. Process Event Data
    try:
        device_id = event.get('device_id', 'UNKNOWN')
        timestamp = event.get('timestamp')
        status = event.get('status', 'N/A')
        # Handle nested metadata safely
        metadata = event.get('metadata', {})
        location = metadata.get('location', 'N/A') if metadata else 'N/A'

        # Format timestamp
        if timestamp:
            dt_object = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        else:
            dt_object = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
    except Exception as e:
        logger.error(f"Data processing error: {e}")
        raise

    # 3. Construct Telegram Message (MarkdownV2 format)
    message_text = (
        f"🚨 *CRITICAL ALERT: {location}* 🚨\n\n"
        f"The pump **{device_id}** has STOPPED.\n"
        f"• Time: `{dt_object}`\n"
        f"• Status: `{status}`"
    )

    payload = {
        'chat_id': telegram_chat_id,
        'text': message_text,
        'parse_mode': 'Markdown' 
    }

    # 4. Send Request using urllib3 (No external dependencies needed)
    try:
        encoded_body = json.dumps(payload).encode('utf-8')
        response = http.request(
            'POST',
            telegram_api_url,
            body=encoded_body,
            headers={'Content-Type': 'application/json'}
        )

        if response.status != 200:
            logger.error(f"Telegram API Error: {response.status} - {response.data.decode('utf-8')}")
            raise RuntimeError(f"Telegram API returned status {response.status}")

        logger.info("Alert sent successfully to Telegram.")
        return {
            'statusCode': 200,
            'body': json.dumps('Alert sent!')
        }

    except Exception as e:
        logger.error(f"Failed to send Telegram request: {e}")
        # Raising an exception here ensures the message goes to the DLQ (Dead Letter Queue)
        raise RuntimeError("Telegram API communication failed")