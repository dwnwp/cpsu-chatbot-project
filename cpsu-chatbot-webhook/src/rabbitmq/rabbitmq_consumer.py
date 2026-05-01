from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, ImageMessage,
    ShowLoadingAnimationRequest
)
from src.http_request.facebook_messaging_request import reply_image_facebook, reply_text_facebook, show_typing_animation_facebook
from src.connector.rabbitmq_connector import get_channel, QUEUE_LINE, QUEUE_FACEBOOK
from src.services import agent_service, conversation_service
from src.models.workflow import WorkflowInput
from settings import Settings as ENV
from src.utils import constvar
import aio_pika
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

# ==================== LINE SDK Config ====================
_line_configuration = Configuration(access_token=ENV.LINE_CHANNEL_ACCESS_TOKEN)


# ==================== Message Processing ====================
async def _process_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    """Process a single message from the queue.

    Multi-turn support:
        Messages from the same user are batched via Redis queue + lock.
        If a user sends multiple messages while AI is processing, they
        get combined into a single request for a coherent response.

    Flow:
        1. Parse message JSON
        2. Push to Redis message queue (per user)
        3. Try to acquire Redis lock
        4. If lock acquired → fetch all queued messages → combine → run AI → reply
        5. If lock not acquired → message sits in Redis, current worker will pick it up
        6. ACK the RabbitMQ message (delivery is guaranteed, Redis handles batching)
    """
    async with message.process(requeue=False):
        try:
            body = json.loads(message.body.decode())
            platform = body["platform"]
            user_id = body["user_id"]
            text = body["text"]
            reply_token = body.get("reply_token")

            logger.info("=" * 80)
            logger.info(f"\033[92m[RABBITMQ] Consumer received [{platform}] user={user_id}: {text[:50]}...\033[0m")

            # Get or create conversation
            conversation_id = await conversation_service.conversation_get_or_create(
                user_id=user_id,
                platform=platform,
            )

            # Handle command
            if text.strip().lower() == "reset":
                conversation_id = await conversation_service.reset_conversation(
                    user_id=user_id,
                    platform=platform,
                )
                reply = "เริ่มต้นคุยเรื่องใหม่ได้เลย!" if conversation_id else "ไม่สามารถรีเซ็ตการสนทนาได้ขณะนี้!"
                await _send_reply(platform, user_id, reply, reply_token)
                return

            # Push to Redis message queue for batching
            await conversation_service.push_message_queue(user_id, platform, text, reply_token)

            # Try to acquire per-user lock
            lock_acquired = await conversation_service.lock_process_running(user_id, platform)

            if lock_acquired:
                logger.info(f"Lock acquired. Processing queue for {user_id}")
                await _process_user_queue(user_id, platform, conversation_id)
            else:
                logger.info(f"Worker busy. Message queued for {user_id}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid message JSON: {e}")
            raise

        except Exception as e:
            logger.exception(f"[RABBITMQ] Consumer error: {e}")
            try:
                body = json.loads(message.body.decode())
                await _send_reply(
                    body.get("platform", ""),
                    body.get("user_id", ""),
                    constvar.MESSAGE_ERROR,
                    body.get("reply_token"),
                )
            except Exception:
                pass
            raise


async def _process_user_queue(user_id: str, platform: str, conversation_id: str):
    """Fetch batched messages from Redis queue, combine, and process.

    Keeps fetching until the queue is empty — handles messages that arrived
    while the AI was processing.
    """
    combined_text = ""
    reply_text = constvar.MESSAGE_ERROR
    image_urls = None
    last_token = None

    loading_task = asyncio.create_task(_keep_loading(user_id, platform))

    try:
        while True:
            doc = await conversation_service.fetch_message_queue(user_id, platform)

            if not doc:
                if last_token or platform == "facebook":
                    await _send_reply(platform, user_id, reply_text, last_token, image_urls)
                break

            queue_batch = doc.get("message_queue", [])

            if not queue_batch:
                if last_token or platform == "facebook":
                    await _send_reply(platform, user_id, reply_text, last_token, image_urls)
                break

            # Combine all queued messages
            combined_text = combined_text + " " + " ".join([msg["text"] for msg in queue_batch])
            last_token = queue_batch[-1].get("reply_token") or last_token

            # Run AI agent workflow
            try:
                workflow_result = await agent_service.run_workflow(
                    WorkflowInput(
                        input_as_text=combined_text.strip(),
                        user_id=user_id,
                        conversation_id=conversation_id,
                        platform=platform,
                    )
                )               
                reply_text = workflow_result.text
                image_urls = workflow_result.image_urls
            except Exception as e:
                logger.error(f"AI workflow error: {e}")

    except Exception as e:
        logger.exception(f"[RABBITMQ] Queue processing crashed: {e}")
        image_urls = None
        if last_token or platform == "facebook":
            try:
                await _send_reply(
                    platform, user_id,
                    constvar.MESSAGE_ERROR,
                    last_token,
                    image_urls
                )
            except Exception:
                pass

    finally:
        loading_task.cancel()
        await conversation_service.unlock_process_running(user_id, platform)
        logger.info(f"Lock released for {user_id}")


# ==================== Reply Routing ====================
async def _send_reply(platform: str, user_id: str, text: str, reply_token: str | None = None, image_urls: list[str] | None = None) -> None:
    """Route reply to the correct platform handler."""
    if platform == "line":
        await _send_line_reply(user_id, text, reply_token, image_urls)
    elif platform == "facebook":
        await _send_facebook_reply(user_id, text, image_urls)
    else:
        logger.warning(f"Unknown platform: {platform}")


async def _send_line_reply(user_id: str, text: str, reply_token: str | None = None, image_urls: list[str] | None = None) -> None:
    """Send reply via LINE using reply_token."""
    if not reply_token:
        logger.warning(f"[LINE] No reply_token for LINE user {user_id}, cannot reply")
        return

    with ApiClient(_line_configuration) as api_client:
        api = MessagingApi(api_client)

        messages = []
        if image_urls:
            for url in image_urls[:4]:  # leave room for text message
                messages.append(ImageMessage(originalContentUrl=url, previewImageUrl=url))
            if len(image_urls) > 4:
                from src.http_request.line_messaging_request import push_line_images
                try:
                    logger.info(f"[LINE] More than 4 images, pushing {len(image_urls)-4} extra images")
                    await push_line_images(
                        channel_access_token=ENV.LINE_CHANNEL_ACCESS_TOKEN,
                        user_id=user_id,
                        image_urls=image_urls[4:]
                    )
                except Exception as e:
                    logger.error(f"[LINE] Failed to push extra images: {e}")

        messages.append(TextMessage(text=text))

        api.reply_message_with_http_info(
            ReplyMessageRequest(reply_token=reply_token, messages=messages[:5])
        )
    logger.info(f"[LINE] reply sent to {user_id}")


async def _send_facebook_reply(user_id: str, text: str, image_urls: list[str] | None = None) -> None:
    """Send reply via Facebook Messenger API."""
    if image_urls:
        await reply_image_facebook(user_id, image_urls)

    await reply_text_facebook(user_id, text)
    logger.info(f"[FACEBOOK] reply sent to {user_id}")


async def _keep_loading(user_id: str, platform: str):
    """Keep showing loading animation while AI is processing."""
    if platform not in ["line", "facebook"]:
        return

    try:
        while True:
            if platform == "line":
                with ApiClient(_line_configuration) as api_client:
                    api = MessagingApi(api_client)
                    api.show_loading_animation(
                        ShowLoadingAnimationRequest(chatId=user_id, loadingSeconds=60)
                    )
                await asyncio.sleep(50)
            elif platform == "facebook":
                await show_typing_animation_facebook(user_id)
                await asyncio.sleep(15)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh loading animation for {user_id}: {e}")


# ==================== Consumer Lifecycle ====================
_consuming = False

async def start_consuming() -> None:
    """Start consuming messages from LINE and Facebook queues."""
    global _consuming
    _consuming = True

    channel = await get_channel()

    line_queue = await channel.get_queue(QUEUE_LINE)
    facebook_queue = await channel.get_queue(QUEUE_FACEBOOK)

    await line_queue.consume(_process_message)
    await facebook_queue.consume(_process_message)

    logger.info("[RABBITMQ] Consumer started — listening on LINE and Facebook queues")


async def stop_consuming() -> None:
    """Stop consuming messages gracefully."""
    global _consuming
    _consuming = False
    logger.info("[RABBITMQ] Consumer stopped")
