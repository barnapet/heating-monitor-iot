import json
import logging
from channel_factory import get_active_channels

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def format_message(status: str, device_id: str) -> str:
    """Business Logic: Forming the message."""
    if status == 'INACTIVE':
        return f"🚨 **ALERT** 🚨\nThe boiler is inactive!\nDevice: `{device_id}`"
    return f"Status info: {status} (Device: {device_id})"

def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")
    
    status = event.get('status', 'UNKNOWN')
    device_id = event.get('device_id', 'n/a')
    message = format_message(status, device_id)

    active_channels = get_active_channels()
    
    if not active_channels:
        raise ValueError("No notification channels configured! Check SSM Parameters.")

    errors = []

    for channel in active_channels:
        try:
            channel.send(message)
        except Exception as e:
            logger.error(f"ERROR sending to {type(channel).__name__}: {e}")
            errors.append(e)

    if errors:
        error_msg = f"Delivery failed for {len(errors)} channels. Triggering AWS Retry/DLQ."
        logger.error(error_msg)
        raise Exception(f"{error_msg} First error: {errors[0]}")

    result_msg = f"Message successfully sent to all {len(active_channels)} configured channels."
    logger.info(result_msg)

    return {
        "statusCode": 200,
        "body": json.dumps(result_msg)
    }