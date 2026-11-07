from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, TypeVar

logger = logging.getLogger("scoutai.retry")

T = TypeVar("T")

# Global semaphore to limit concurrent requests to Gemini / external APIs
GLOBAL_LLM_SEMAPHORE = asyncio.Semaphore(3)


class QuotaExceededError(RuntimeError):
    """Raised when the maximum LLM call budget for a single run is exceeded."""

    pass


async def with_retry(
    func: Callable[[], Coroutine[Any, Any, T]],
    max_retries: int = 4,
    initial_delay: float = 1.5,
    backoff_factor: float = 2.0,
    semaphore: asyncio.Semaphore = GLOBAL_LLM_SEMAPHORE,
) -> T:
    """
    Executes an async function within a concurrency semaphore, applying
    exponential backoff retry for transient network errors and rate limit (429) errors.
    """
    delay = initial_delay
    last_error: Exception | None = None

    async with semaphore:
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                is_rate_limit = (
                    "429" in err_str
                    or "resource_exhausted" in err_str
                    or "quota" in err_str
                    or "too many requests" in err_str
                )
                is_transient = (
                    "timeout" in err_str
                    or "connection" in err_str
                    or "503" in err_str
                    or "500" in err_str
                )

                if (is_rate_limit or is_transient) and attempt < max_retries:
                    wait_time = delay * (backoff_factor**attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed with {type(e).__name__}: {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
        if last_error:
            raise last_error
        raise RuntimeError("Retry loop completed without return or exception")
