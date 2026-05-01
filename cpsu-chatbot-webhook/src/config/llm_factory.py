import logging
from settings import Settings as ENV
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

def get_llm(model_name: str, **kwargs) -> BaseChatModel:
    """Instantiate a ChatModel based on the LLM_PROVIDER specified in .env."""
    provider = ENV.LLM_PROVIDER
    logger.info(f"Initializing LLM Provider: {provider.upper()} | Model: {model_name}")

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(base_url=ENV.OLLAMA_BASE_URL, model=model_name, keep_alive="5m", **kwargs)
    
    # elif provider == "openai":
    #     from langchain_openai import ChatOpenAI
    #     return ChatOpenAI(model=model_name, api_key=ENV.OPENAI_API_KEY, **kwargs)
        
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_embeddings() -> Embeddings:
    """Instantiate Embeddings based on the EMBEDDING_PROVIDER specified in .env."""
    provider = ENV.EMBEDDING_PROVIDER
    model_name = ENV.EMBEDDING_MODEL_NAME
    logger.info(f"Initializing Embedding Provider: {provider.upper()} | Model: {model_name}")

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(base_url=ENV.OLLAMA_BASE_URL, model=model_name)
        
    # elif provider == "openai":
    #     from langchain_openai import OpenAIEmbeddings
    #     return OpenAIEmbeddings(model=model_name, api_key=ENV.OPENAI_API_KEY)
        
    else:
        raise ValueError(f"Unsupported Embedding provider: {provider}")
