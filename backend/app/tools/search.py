from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from duckduckgo_search import DDGS
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.services.cache_service import CacheService

logger = logging.getLogger("scoutai.tools.search")
settings = get_settings()


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search the web for a query and return structured results."""
        pass


class DuckDuckGoSearchProvider(SearchProvider):
    def __init__(self) -> None:
        pass

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        cache_key = f"ddg:{query.strip().lower()}:{max_results}"
        cached = CacheService.get(cache_key, category="search")
        if cached and isinstance(cached, list):
            logger.info(f"Returning {len(cached)} cached DuckDuckGo results for: {query}")
            return [SearchResult(**r) for r in cached]

        def _do_search() -> List[SearchResult]:
            results: List[SearchResult] = []
            try:
                with DDGS(timeout=4) as ddgs:
                    raw_results = list(ddgs.text(query, max_results=max_results))
                    for item in raw_results:
                        title = item.get("title", "")
                        url = item.get("href") or item.get("link", "")
                        snippet = item.get("body") or item.get("snippet", "")
                        if url:
                            results.append(SearchResult(title=title, url=url, snippet=snippet))
            except Exception as e:
                logger.warning(f"DuckDuckGo search error for query '{query}': {e}")
            return results

        results = await asyncio.to_thread(_do_search)

        if results:
            CacheService.set(cache_key, category="search", data=[r.model_dump() for r in results])
        return results


class TavilySearchProvider(SearchProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        cache_key = f"tavily:{query.strip().lower()}:{max_results}"
        cached = CacheService.get(cache_key, category="search")
        if cached and isinstance(cached, list):
            logger.info(f"Returning {len(cached)} cached Tavily results for: {query}")
            return [SearchResult(**r) for r in cached]

        results: List[SearchResult] = []
        try:
            from tavily import AsyncTavilyClient

            client = AsyncTavilyClient(api_key=self.api_key)
            resp = await client.search(query=query, max_results=max_results, search_depth="basic")
            for item in resp.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                    )
                )
        except Exception as e:
            logger.warning(f"Tavily search error for query '{query}': {e}")

        if results:
            CacheService.set(cache_key, category="search", data=[r.model_dump() for r in results])
        return results


_mock_search_provider: Optional[SearchProvider] = None


def set_mock_search_provider(provider: Optional[SearchProvider]) -> None:
    global _mock_search_provider
    _mock_search_provider = provider


def get_search_provider(override_key: Optional[str] = None) -> SearchProvider:
    """Returns the configured SearchProvider instance or mock provider if set."""
    if _mock_search_provider is not None:
        return _mock_search_provider
    tavily_key = override_key or settings.TAVILY_API_KEY
    if tavily_key:
        return TavilySearchProvider(api_key=tavily_key)
    return DuckDuckGoSearchProvider()
