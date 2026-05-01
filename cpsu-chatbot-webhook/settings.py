from os import getenv

class Settings:
    # ==================== LINE ====================
    LINE_CHANNEL_ACCESS_TOKEN: str = getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_CHANNEL_SECRET: str = getenv("LINE_CHANNEL_SECRET")

    # ==================== MODEL ROUTING ====================
    LLM_PROVIDER: str = getenv("LLM_PROVIDER").lower()
    LLM_MODEL_NAME: str = getenv("LLM_MODEL_NAME")
    
    EMBEDDING_PROVIDER: str = getenv("EMBEDDING_PROVIDER").lower()
    EMBEDDING_MODEL_NAME: str = getenv("EMBEDDING_MODEL_NAME")
    VECTOR_DIMENSION: int = int(getenv("VECTOR_DIMENSION", "1024"))

    # ==================== PROVIDER CONFIGS ====================
    # Ollama
    OLLAMA_BASE_URL: str = getenv("OLLAMA_BASE_URL")
    
    # API Keys
    # OPENAI_API_KEY: str = getenv("OPENAI_API_KEY")

    # ==================== LANGSMITH ====================
    LANGCHAIN_API_KEY: str = getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = getenv("LANGCHAIN_PROJECT")
    LANGCHAIN_TRACING_V2: str = getenv("LANGCHAIN_TRACING_V2")

    # ==================== REDIS ====================
    REDIS_URL: str = getenv("REDIS_URL")
    SEMANTIC_CACHE_THRESHOLD: float = float(getenv("SEMANTIC_CACHE_THRESHOLD", "0.2"))
    SEMANTIC_CACHE_TTL: int = int(getenv("SEMANTIC_CACHE_TTL", "86400"))

    # ==================== FAECBOOK ====================
    FACEBOOK_TOKEN: str = getenv("FACEBOOK_TOKEN")
    FACEBOOK_VERIFY_TOKEN: str = getenv("FACEBOOK_VERIFY_TOKEN")
    FACEBOOK_PAGE_ID: str = getenv("FACEBOOK_PAGE_ID")

    # ==================== QDRANT ====================
    QDRANT_HOST: str = getenv("QDRANT_HOST")
    QDRANT_PORT: int = int(getenv("QDRANT_PORT"))

    # ==================== RABBITMQ ====================
    RABBITMQ_HOST: str = getenv("RABBITMQ_HOST")
    RABBITMQ_PORT: int = int(getenv("RABBITMQ_PORT"))
    RABBITMQ_USER: str = getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = getenv("RABBITMQ_PASSWORD")
    RABBITMQ_VHOST: str = getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_PREFETCH: int = int(getenv("RABBITMQ_PREFETCH", "10"))

    # ==================== CLOUD ====================
    MINIO_ENDPOINT: str = getenv("MINIO_ENDPOINT")
    MINIO_EXTERNAL_ENDPOINT: str = getenv("MINIO_EXTERNAL_ENDPOINT")
    MINIO_ACCESS_KEY: str = getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = getenv("MINIO_BUCKET_NAME")
    MINIO_USE_SSL: str = getenv("MINIO_USE_SSL", "false")
    MINIO_REGION: str = getenv("MINIO_REGION")
