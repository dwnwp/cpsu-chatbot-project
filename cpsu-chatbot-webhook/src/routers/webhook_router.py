from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from src.handlers.line_event_handler import handle_line_webhook
from src.handlers.facebook_event_handler import handle_facebook_webhook
from src.connector.rabbitmq_connector import is_connected as rabbitmq_is_connected
from src.connector.redis_connector import AsyncRedisConnector
from settings import Settings as ENV
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/adapter", tags=["Webhooks"])


# ==================== Health Check ====================
@router.get("/health", response_class=JSONResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    checks = {}

    # Redis
    try:
        redis_client = AsyncRedisConnector().client
        checks["redis"] = await redis_client.ping()
    except Exception:
        checks["redis"] = False

    # RabbitMQ
    try:
        checks["rabbitmq"] = rabbitmq_is_connected()
    except Exception:
        checks["rabbitmq"] = False

    all_healthy = all(checks.values())
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks,
        },
    )

# ==================== LINE Webhook ====================
@router.post("/line", response_class=JSONResponse)
async def webhook_line(request: Request):
    """Handle LINE webhook events."""

    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        await handle_line_webhook(body_text, signature)

    except Exception as e:
        logger.error(f"[LINE] webhook error: {e}")
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid signature"}
        )

    return JSONResponse(
        status_code=200, 
        content={"message": "OK"}
    )


# ==================== Facebook Webhook ====================
@router.get("/facebook")
async def webhook_facebook_verify(request: Request):
    """Facebook webhook verification."""

    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if verify_token == ENV.FACEBOOK_VERIFY_TOKEN:
        return PlainTextResponse(
            status_code=200,
            content=challenge or ""
        )

    return JSONResponse(
        status_code=403,
        content={"message": "Invalid verify token"}
    )


@router.post("/facebook", response_class=JSONResponse)
async def webhook_facebook(request: Request):
    """Handle Facebook webhook events — publish to RabbitMQ for async processing."""

    body = await request.json()

    try:
        await handle_facebook_webhook(body)

    except Exception as e:
        logger.error(f"[FACEBOOK] webhook error: {e}")
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid signature"}
        )

    return JSONResponse(
        status_code=200, 
        content={"message": "OK"}
    )
