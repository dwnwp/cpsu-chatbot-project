from src.services.knowledge_retrieval_service import get_retrieval_service
from src.services.agent_summarize_service import summarize_context, summarize_staff_context
from src.utils.constvar import MESSAGE_NO_ANSWER_FALLBACK
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from typing import Literal
import logging


logger = logging.getLogger(__name__)

retrieval_service = get_retrieval_service()

@tool
async def finance_search_tool(
    user_question: str,
    config: RunnableConfig,
    program_type: Literal["regular", "special"] = "regular",
    study_level: Literal["bachelor", "master", "doctoral"] = "bachelor",
) -> str:
    """Search financial/tuition information. Use this tool when user asks about tuition fees, scholarships, or financial matters.
    
    Args:
        program_type: The user's program type (regular, special)
        study_level: The user's study level (bachelor, master, or doctoral)
        user_question: The user's question to search for
    """
    if not program_type or program_type.lower() == "none" or program_type.lower() == "null" or program_type.lower() == "n/a":
        program_type = "regular"
    if not study_level or study_level.lower() == "none" or study_level.lower() == "null" or study_level.lower() == "n/a":
        study_level = "bachelor"
    logger.info("finance_search_tool called with user_question=%s, program_type=%s, study_level=%s",
                user_question, program_type, study_level)
    
    search_filter = {"program_type": program_type, "study_level": study_level}

    retrieved_docs = await retrieval_service.retrieve_multi_query(
        query=user_question,
        user_question=user_question,
        index_name="tuition-fee",
        top_k=5,
        filter=search_filter
    )
    chat_history = config.get("metadata", {}).get("chat_history", [])
    answer = await summarize_context(user_question, user_question, retrieved_docs, chat_history)
    
    if not answer:
        logger.info("[Fallback] finance_search_tool found no answer, checking FAQ database")
        faq_docs = await retrieval_service.retrieve_multi_query(
            query=user_question, 
            user_question=user_question,
            index_name="general", 
            top_k=3
        )
        fallback_answer = await summarize_context(user_question, user_question, faq_docs, chat_history)
        if not fallback_answer:
            return MESSAGE_NO_ANSWER_FALLBACK
        return fallback_answer

    return answer


@tool
async def academic_search_tool(user_question: str, config: RunnableConfig) -> str:
    """Search academic information. Use this tool when user asks about courses, curricula, academic calendar, or academic policies.

    Args:
        user_question: The user's question to search for
    """
    user_question = user_question or config.get("metadata", {}).get("input", "")
    actual_question = config.get("metadata", {}).get("input", "")
    logger.info("academic_search_tool called with user_question=%s", user_question)

    retrieved_docs = await retrieval_service.retrieve_multi_query(
        query=user_question,
        user_question=actual_question,
        index_name="academic",
        top_k=3,
    )
    chat_history = config.get("metadata", {}).get("chat_history", [])
    answer = await summarize_context(user_question, actual_question, retrieved_docs, chat_history)
    
    if not answer:
        logger.info("[Fallback] academic_search_tool found no answer, checking FAQ database")
        faq_docs = await retrieval_service.retrieve_multi_query(
            query=user_question, 
            user_question=actual_question,
            index_name="general", 
            top_k=3
        )
        fallback_answer = await summarize_context(user_question, actual_question, faq_docs, chat_history)
        if not fallback_answer:
            return MESSAGE_NO_ANSWER_FALLBACK
        return fallback_answer

    return answer


@tool
async def staff_search_tool(user_question: str, config: RunnableConfig) -> str:
    """Search staff information. Use this tool when user asks about faculty members, staff contacts, or personnel.

    Args:
        user_question: The user's question to search for
    """
    user_question = user_question or config.get("metadata", {}).get("input", "")
    actual_question = config.get("metadata", {}).get("input", "")
    logger.info("staff_search_tool called with user_question=%s", user_question)

    retrieved_docs = await retrieval_service.retrieve_multi_query(
        query=user_question,
        user_question=actual_question,
        index_name="staff",
        top_k=30,
    )
    chat_history = config.get("metadata", {}).get("chat_history", [])
    answer = await summarize_staff_context(user_question, actual_question, retrieved_docs, config, chat_history)
    
    if not answer:
        logger.info("[Fallback] staff_search_tool found no answer, checking FAQ database")
        faq_docs = await retrieval_service.retrieve_multi_query(
            query=user_question,
            user_question=actual_question,
            index_name="general", 
            top_k=3
        )
        fallback_answer = await summarize_context(user_question, actual_question, faq_docs, chat_history)
        if not fallback_answer:
            return MESSAGE_NO_ANSWER_FALLBACK
        return fallback_answer

    return answer


@tool
async def faq_search_tool(user_question: str, config: RunnableConfig) -> str:
    """Search FAQ/general information. Use this tool when user asks general questions.

    Args:
        user_question: The user's question to search for
    """
    user_question = user_question or config.get("metadata", {}).get("input", "")
    actual_question = config.get("metadata", {}).get("input", "")
    logger.info("faq_search_tool called with user_question=%s", user_question)

    retrieved_docs = await retrieval_service.retrieve_multi_query(
        query=user_question,
        user_question=actual_question,
        index_name="general",
        top_k=3,
    )
    chat_history = config.get("metadata", {}).get("chat_history", [])
    answer = await summarize_context(user_question, actual_question, retrieved_docs, chat_history)
    
    if not answer:
        return MESSAGE_NO_ANSWER_FALLBACK

    return answer