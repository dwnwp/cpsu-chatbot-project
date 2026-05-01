import aio_pika
import json
import logging
from src.connector.rabbitmq_connector import (
    get_channel,
    EXCHANGE_NAME,
    ROUTING_KEY_LINE,
    ROUTING_KEY_FACEBOOK,
)


logger = logging.getLogger(__name__)


async def publish_message(
    platform: str,
    user_id: str,
    text: str,
    reply_token: str | None = None,
) -> None:
    """Publish a webhook message to RabbitMQ for async processing.

    Args:
        platform: 'line' or 'facebook'
        user_id: The user's platform ID
        text: The incoming message text
        reply_token: LINE reply token (optional)
    """
    channel = await get_channel()
    exchange = await channel.get_exchange(EXCHANGE_NAME)

    routing_key = ROUTING_KEY_LINE if platform == "line" else ROUTING_KEY_FACEBOOK

    payload = json.dumps({
        "platform": platform,
        "user_id": user_id,
        "text": text,
        "reply_token": reply_token,
    })

    message = aio_pika.Message(
        body=payload.encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        content_type="application/json",
    )

    await exchange.publish(message, routing_key=routing_key)
    logger.info(f"[RABBITMQ] Published to [{routing_key}] for user {user_id}")
