from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import delete, select

from backend.app.config import get_settings
from backend.app.db import SessionLocal
from backend.app.models import CacheEntry

settings = get_settings()


class CacheService:
    @staticmethod
    def get(cache_key: str, category: str) -> Optional[Any]:
        """Retrieves cached data if present and not expired."""
        with SessionLocal() as db:
            entry = db.scalar(
                select(CacheEntry).where(
                    CacheEntry.cache_key == cache_key,
                    CacheEntry.category == category,
                )
            )
            if not entry:
                return None

            # Check expiration
            expiration_delta = timedelta(hours=settings.CACHE_EXPIRATION_HOURS)
            now = datetime.now(timezone.utc)
            created_at = entry.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            if now - created_at > expiration_delta:
                db.execute(delete(CacheEntry).where(CacheEntry.cache_key == cache_key))
                db.commit()
                return None

            try:
                return json.loads(entry.data_json)
            except Exception:
                return entry.data_json

    @staticmethod
    def set(cache_key: str, category: str, data: Any) -> None:
        """Stores data in the cache with the current timestamp."""
        payload_str = json.dumps(data) if not isinstance(data, str) else data
        with SessionLocal() as db:
            existing = db.scalar(select(CacheEntry).where(CacheEntry.cache_key == cache_key))
            now = datetime.now(timezone.utc)
            if existing:
                existing.category = category
                existing.data_json = payload_str
                existing.created_at = now
            else:
                entry = CacheEntry(
                    cache_key=cache_key,
                    category=category,
                    data_json=payload_str,
                    created_at=now,
                )
                db.add(entry)
            db.commit()
