from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, StickerMessage,
    ShowLoadingAnimationRequest,
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent,
    StickerMessageContent, ImageMessageContent,
)
from linebot.v3.exceptions import InvalidSignatureError
from src.rabbitmq.rabbitmq_publisher import publish_message
from src.utils import constvar
from src.utils.cache import AsyncRateLimiter
from settings import Settings as ENV
import logging
import asyncio


logger = logging.getLogger(__name__)

# ==================== LINE SDK Config ====================
configuration = Configuration(access_token=ENV.LINE_CHANNEL_ACCESS_TOKEN)
_webhook_handler = WebhookHandler(ENV.LINE_CHANNEL_SECRET)

# ==================== Rate Limiting (Redis-backed) ====================
RATE_LIMITER = AsyncRateLimiter()

# ==================== Pending Tasks ====================
_pending_tasks: list = []


# ==================== Webhook Entry Point ====================
async def handle_line_webhook(body: str, signature: str):
    """Handle LINE webhook (async entry point)."""
    global _pending_tasks
    _pending_tasks = []

    try:
        _webhook_handler.handle(body, signature)

        if _pending_tasks:
            await asyncio.gather(*_pending_tasks)

    except InvalidSignatureError:
        logger.error("Invalid LINE signature")
        raise


# ==================== Event Handler ====================
@_webhook_handler.add(MessageEvent)
def handle_event(event: MessageEvent):
    """Handle LINE message event — queue async task for later execution."""
    global _pending_tasks
    _pending_tasks.append(_handle_event_async(event))


async def _handle_event_async(event: MessageEvent):
    """Async event dispatcher with Redis-backed rate limiting."""
    user_id = event.source.user_id
    message = event.message

    if not await RATE_LIMITER.check(user_id):
        with ApiClient(configuration) as api_client:
            api = MessagingApi(api_client)
            api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=constvar.MESSAGE_RATELIMIT)],
                )
            )
        return

    if isinstance(message, TextMessageContent):
        with ApiClient(configuration) as api_client:
            api = MessagingApi(api_client)
            api.show_loading_animation(
                ShowLoadingAnimationRequest(chatId=user_id, loadingSeconds=60)
            )
        await _handle_text(user_id, event.reply_token, message)

    elif isinstance(message, StickerMessageContent):
        with ApiClient(configuration) as api_client:
            api = MessagingApi(api_client)
            _handle_sticker(api, event.reply_token)

    elif isinstance(message, ImageMessageContent):
        with ApiClient(configuration) as api_client:
            api = MessagingApi(api_client)
            _handle_image(api, event.reply_token)


# ==================== Message Handlers ====================
async def _handle_text(user_id: str, reply_token: str, message: TextMessageContent):
    """Handle text message — publish to RabbitMQ."""
    text = message.text
    await publish_message(
        platform="line",
        user_id=user_id,
        text=text,
        reply_token=reply_token,
    )
    logger.info(f"[LINE] message published to RabbitMQ for user {user_id}")


def _handle_sticker(api: MessagingApi, reply_token: str):
    """Handle sticker message — reply with a fixed sticker."""
    api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[StickerMessage(packageId="11537", stickerId="52002736")],
        )
    )


def _handle_image(api: MessagingApi, reply_token: str):
    """Handle image message — reply with text."""
    api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=constvar.MESSAGE_SEND_IMAGE)],
        )
    )
