from dotenv import load_dotenv
from os import getenv
from src.config.logging import setup_logging

load_dotenv()
setup_logging()

import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.routers.webhook_router import router as webhook_router
from src.http_request import close_http_client
from src.connector.rabbitmq_connector import setup_topology, close_connection as close_rabbitmq
from src.rabbitmq.rabbitmq_consumer import start_consuming, stop_consuming


logger = logging.getLogger(__name__)


# ==================== Lifespan ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    logger.info("Starting CPSU Chatbot Webhook Server...")

    # Initialize RabbitMQ
    try:
        await setup_topology()
        await start_consuming()
        logger.info("[RabbitMQ] RabbitMQ consumer started")
    except Exception as e:
        logger.error(f"[RabbitMQ] Failed to initialize RabbitMQ: {e}")
        logger.warning("[RabbitMQ] Server will start without RabbitMQ — messages will fail to publish")

    yield

    # Cleanup
    await stop_consuming()
    await close_rabbitmq()
    await close_http_client()
    logger.info("Shutting down CPSU Chatbot Webhook Server...")


# ==================== App ====================
app = FastAPI(
    title="CPSU Chatbot Webhook",
    description="Multi-agent RAG chatbot for CPSU",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(webhook_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(getenv("PORT_WEBHOOK", 8000)),
        reload=False,
    )
