import aio_pika
import logging
from settings import Settings as ENV


logger = logging.getLogger(__name__)


# ==================== Singleton Connection ====================
_connection: aio_pika.abc.AbstractRobustConnection | None = None
_channel: aio_pika.abc.AbstractRobustChannel | None = None

# ==================== Exchange & Queue Names ====================
EXCHANGE_NAME = "webhook_exchange"
DLX_EXCHANGE_NAME = "webhook_dlx"

QUEUE_LINE = "webhook.line.messages"
QUEUE_FACEBOOK = "webhook.facebook.messages"
QUEUE_DEAD_LETTERS = "webhook.dead_letters"

ROUTING_KEY_LINE = "line"
ROUTING_KEY_FACEBOOK = "facebook"


async def get_connection() -> aio_pika.abc.AbstractRobustConnection:
    """Get or create singleton RabbitMQ connection."""
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(
            host=ENV.RABBITMQ_HOST,
            port=ENV.RABBITMQ_PORT,
            login=ENV.RABBITMQ_USER,
            password=ENV.RABBITMQ_PASSWORD,
            virtualhost=ENV.RABBITMQ_VHOST,
        )
        logger.info("[RabbitMQ] RabbitMQ connection established")
    return _connection


async def get_channel() -> aio_pika.abc.AbstractRobustChannel:
    """Get or create singleton RabbitMQ channel."""
    global _channel
    if _channel is None or _channel.is_closed:
        connection = await get_connection()
        _channel = await connection.channel()
        await _channel.set_qos(prefetch_count=ENV.RABBITMQ_PREFETCH)
        logger.info("[RabbitMQ] RabbitMQ channel created (prefetch={})".format(ENV.RABBITMQ_PREFETCH))
    return _channel


async def setup_topology():
    """Declare exchanges, queues, and bindings on startup.
    
    Topology:
        webhook_exchange (direct, durable)
            ├── routing_key=line     → webhook.line.messages     (durable, DLX)
            └── routing_key=facebook → webhook.facebook.messages (durable, DLX)
        
        webhook_dlx (fanout, durable)
            └── webhook.dead_letters (durable)
    """
    channel = await get_channel()

    # ── Dead Letter Exchange ──
    dlx_exchange = await channel.declare_exchange(
        DLX_EXCHANGE_NAME,
        aio_pika.ExchangeType.FANOUT,
        durable=True,
    )
    dlx_queue = await channel.declare_queue(
        QUEUE_DEAD_LETTERS,
        durable=True,
    )
    await dlx_queue.bind(dlx_exchange)
    logger.info("[RabbitMQ] DLX exchange and queue declared")

    # ── Main Exchange ──
    main_exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    # ── LINE Queue ──
    line_queue = await channel.declare_queue(
        QUEUE_LINE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DLX_EXCHANGE_NAME,
            "x-message-ttl": 1800000,   # 80 minutes (AI processing timeout)
            "x-max-length": 10000,
        },
    )
    await line_queue.bind(main_exchange, routing_key=ROUTING_KEY_LINE)

    # ── Facebook Queue ──
    facebook_queue = await channel.declare_queue(
        QUEUE_FACEBOOK,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DLX_EXCHANGE_NAME,
            "x-message-ttl": 1800000,
            "x-max-length": 10000,
        },
    )
    await facebook_queue.bind(main_exchange, routing_key=ROUTING_KEY_FACEBOOK)

    logger.info("[RabbitMQ] RabbitMQ topology setup complete")
    return main_exchange, line_queue, facebook_queue


async def close_connection():
    """Close RabbitMQ connection gracefully."""
    global _connection, _channel
    if _channel and not _channel.is_closed:
        await _channel.close()
        _channel = None
    if _connection and not _connection.is_closed:
        await _connection.close()
        _connection = None
    logger.info("[RabbitMQ] RabbitMQ connection closed")


def is_connected() -> bool:
    """Check if RabbitMQ connection is alive (for health checks)."""
    return _connection is not None and not _connection.is_closed
