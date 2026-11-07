from __future__ import annotations

import json
import logging
import os
from typing import Any, Callable, Optional, Type, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.utils.retry import GLOBAL_LLM_SEMAPHORE, QuotaExceededError, with_retry

logger = logging.getLogger("scoutai.services.llm")
settings = get_settings()

T = TypeVar("T", bound=BaseModel)

# Configurable mock handler for deterministic unit & agent testing
_mock_llm_handler: Optional[Callable[[Type[BaseModel], str, str], Any]] = None


def set_mock_llm(handler: Optional[Callable[[Type[BaseModel], str, str], Any]]) -> None:
    global _mock_llm_handler
    _mock_llm_handler = handler


def get_mock_llm() -> Optional[Callable[[Type[BaseModel], str, str], Any]]:
    return _mock_llm_handler


def init_langsmith() -> None:
    """Configures LangSmith tracing if an API key is available."""
    if settings.LANGSMITH_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        logger.info(f"LangSmith tracing enabled for project: {settings.LANGSMITH_PROJECT}")


def get_gemini_chat_model(model_name: Optional[str] = None):
    """Initializes and returns the ChatGoogleGenerativeAI model."""
    init_langsmith()
    api_key = settings.effective_gemini_key
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY is not set.")

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL,
        google_api_key=api_key,
        temperature=0.2,
        max_retries=2,
    )


async def call_structured_llm(
    schema: Type[T],
    system_prompt: str,
    user_prompt: str,
    call_tracker: Optional[dict] = None,
    model_name: Optional[str] = None,
) -> T:
    """
    Executes a structured LLM call ensuring:
    1. Budget enforcement (MAX_LLM_CALLS_PER_RUN).
    2. Concurrency limiting and exponential backoff retry.
    3. Auto-retry on schema validation failure (max 2 attempts).
    4. Mock support during automated test runs.
    """
    # Check mock handler first
    if _mock_llm_handler is not None:
        if call_tracker is not None:
            call_tracker["calls"] = call_tracker.get("calls", 0) + 1
        res = _mock_llm_handler(schema, system_prompt, user_prompt)
        if isinstance(res, schema):
            return res
        elif isinstance(res, dict):
            return schema.model_validate(res)
        return res

    # Budget cap check
    if call_tracker is not None:
        current_calls = call_tracker.get("calls", 0)
        if current_calls >= settings.MAX_LLM_CALLS_PER_RUN:
            raise QuotaExceededError(
                f"Run exceeded maximum LLM call budget of {settings.MAX_LLM_CALLS_PER_RUN} calls."
            )
        call_tracker["calls"] = current_calls + 1

    llm = get_gemini_chat_model(model_name)
    structured_llm = llm.with_structured_output(schema)

    validation_errors = 0
    max_validation_attempts = 2

    async def _invoke() -> T:
        nonlocal validation_errors
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        try:
            return await structured_llm.ainvoke(messages)
        except Exception as e:
            # If schema validation failed, try with JSON parsing fallback
            if validation_errors < max_validation_attempts:
                validation_errors += 1
                logger.warning(
                    f"Structured invocation validation error: {e}. Retrying with raw JSON extraction..."
                )
                raw_resp = await llm.ainvoke(messages)
                raw_c = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                if isinstance(raw_c, list):
                    text = "".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in raw_c)
                else:
                    text = str(raw_c)
                # Attempt to extract JSON markdown block
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                parsed = json.loads(text)
                return schema.model_validate(parsed)
            raise

    return await with_retry(_invoke, semaphore=GLOBAL_LLM_SEMAPHORE)
