from src.utils.cache import TTLOrderedDict, AsyncRateLimiter
from src.rabbitmq.rabbitmq_publisher import publish_message
from src.http_request.facebook_messaging_request import reply_text_facebook, show_typing_animation_facebook
from src.utils import constvar
import logging


logger = logging.getLogger(__name__)

# ==================== Deduplication & Rate Limiting ====================
PROCESSED_MIDS = TTLOrderedDict(max_size=10000, ttl_seconds=3600)
RATE_LIMITER = AsyncRateLimiter()


async def handle_facebook_webhook(body: dict):
    """Handle Facebook webhook (async entry point)."""
    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            if "message" not in event:
                continue

            msg = event["message"]
            uid = event["sender"]["id"]
            mid = msg.get("mid")

            # Deduplicate
            if mid and mid in PROCESSED_MIDS:
                logger.info(f"[FACEBOOK] Duplicate MID ignored: {mid}")
                continue

            if not await RATE_LIMITER.check(uid):
                logger.info(f"[FACEBOOK] Rate limited user: {uid}")
                try:
                    await reply_text_facebook(uid, constvar.MESSAGE_RATELIMIT)
                except Exception:
                    pass
                continue

            if mid:
                PROCESSED_MIDS.add(mid)

            # Display typing animation
            await show_typing_animation_facebook(uid)

            attachments = msg.get("attachments", [])
            is_sticker = False
            is_image = False

            for attachment in attachments:
                if attachment.get("type") == "image":
                    payload = attachment.get("payload", {})
                    if "sticker_id" in payload:
                        is_sticker = True
                    else:
                        is_image = True

            # Handle Stickers
            if is_sticker:
                try:
                    await _handle_sticker(uid)
                except Exception as e:
                    logger.error(f"[FACEBOOK] sticker reply error: {e}")
                continue

            # Handle Images
            if is_image:
                try:
                    await _handle_image(uid)
                except Exception as e:
                    logger.error(f"[FACEBOOK] image reply error: {e}")
                continue

            # Handle Text
            text = msg.get("text")
            if not text:
                continue
            try:
                await _handle_text(uid=uid, message=text)
            except Exception as e:
                logger.error(f"[FACEBOOK] text reply error: {e}")


async def _handle_text(uid: str, message: str):
    """Handle text message — publish to RabbitMQ."""
    await publish_message(platform="facebook", user_id=uid, text=message)
    logger.info(f"[FACEBOOK] message published to RabbitMQ for user {uid}")


async def _handle_sticker(uid: str):
    """Handle sticker message"""
    await reply_text_facebook(uid, "😉")


async def _handle_image(uid: str):
    """Handle image message"""
    await reply_text_facebook(uid, constvar.MESSAGE_SEND_IMAGE)