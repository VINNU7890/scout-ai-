from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List

from fastapi import HTTPException, Request, status

from backend.app.config import get_settings

settings = get_settings()

# In-memory timestamp buckets per IP
_ip_request_timestamps: Dict[str, List[float]] = defaultdict(list)


def check_rate_limit(request: Request) -> None:
    """
    Checks per-IP rate limits using a 60-second sliding window.
    Raises HTTPException 429 if the request limit is exceeded.
    """
    limit = settings.RATE_LIMIT_PER_MINUTE
    if limit <= 0:
        return

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - 60.0

    # Prune old timestamps
    timestamps = [t for t in _ip_request_timestamps[client_ip] if t > window_start]
    timestamps.append(now)
    _ip_request_timestamps[client_ip] = timestamps

    if len(timestamps) > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": f"Rate limit of {limit} requests per minute exceeded.",
                }
            },
        )
