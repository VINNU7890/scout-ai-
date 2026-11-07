from __future__ import annotations

import asyncio
import logging
import urllib.parse
from abc import ABC, abstractmethod
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.services.cache_service import CacheService

logger = logging.getLogger("scoutai.tools.search")
settings = get_settings()

BROWSER_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


def clean_search_query(q: str) -> str:
    """Converts verbose natural-language questions into high-signal search keywords."""
    stop_words = {
        "what", "is", "the", "how", "does", "are", "recent", "latest", "including",
        "and", "for", "in", "of", "to", "a", "an", "tell", "me", "about", "can", "you",
        "give", "details", "overview", "between", "btw", "vs", "versus", "comparison",
    }
    words = [w.strip("?,.:;\"'()[]{}!") for w in q.split()]
    filtered = [w for w in words if w.lower() not in stop_words and len(w) > 1]
    if len(filtered) >= 2:
        return " ".join(filtered[:8])
    return q.strip()


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

        cleaned_q = clean_search_query(query)

        # 1. Primary: Direct HTML DuckDuckGo search (fast, real-time, resilient)
        results = await self._search_html(cleaned_q, max_results=max_results)

        # 2. If HTML returned 0, try original uncleaned query on HTML
        if not results and cleaned_q != query:
            results = await self._search_html(query, max_results=max_results)

        # 3. If still empty, attempt DDGS python library
        if not results:
            results = await self._search_ddgs_library(cleaned_q, max_results=max_results)

        # 4. If still empty, fall back to Wikipedia search for entity background
        if not results:
            results = await self._search_wikipedia(cleaned_q, max_results=max_results)

        if results:
            CacheService.set(cache_key, category="search", data=[r.model_dump() for r in results])
        return results

    async def _search_html(self, query: str, max_results: int = 5) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {
                "User-Agent": BROWSER_USER_AGENTS[0],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for div in soup.find_all("div", class_="result"):
                        title_elem = div.find("a", class_="result__a")
                        snippet_elem = div.find("a", class_="result__snippet")
                        if title_elem and snippet_elem:
                            raw_url = title_elem.get("href", "")
                            if "uddg=" in raw_url:
                                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                                clean_url = parsed.get("uddg", [raw_url])[0]
                            else:
                                clean_url = raw_url

                            title = title_elem.get_text().strip()
                            snippet = snippet_elem.get_text().strip()
                            if clean_url and snippet:
                                results.append(
                                    SearchResult(title=title, url=clean_url, snippet=snippet)
                                )
                                if len(results) >= max_results:
                                    break
        except Exception as e:
            logger.debug(f"Direct DDG HTML search error for '{query}': {e}")
        return results

    async def _search_ddgs_library(self, query: str, max_results: int = 5) -> List[SearchResult]:
        def _do_search() -> List[SearchResult]:
            res: List[SearchResult] = []
            try:
                with DDGS(timeout=8) as ddgs:
                    raw_results = list(ddgs.text(query, max_results=max_results))
                    for item in raw_results:
                        title = item.get("title", "")
                        url = item.get("href") or item.get("link", "")
                        snippet = item.get("body") or item.get("snippet", "")
                        if url and snippet:
                            res.append(SearchResult(title=title, url=url, snippet=snippet))
            except Exception as e:
                logger.debug(f"DDGS library search error for query '{query}': {e}")
            return res

        return await asyncio.to_thread(_do_search)

    async def _search_wikipedia(self, query: str, max_results: int = 3) -> List[SearchResult]:
        results: List[SearchResult] = []
        try:
            entity = " ".join(query.split()[:2])
            url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(entity)}&limit={max_results}&format=json"
            headers = {"User-Agent": "ScoutAI-ResearchAgent/1.0 (https://scoutai.local)"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    titles = data[1] if len(data) > 1 else []
                    urls = data[3] if len(data) > 3 else []
                    for t, u in zip(titles, urls):
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(t)}"
                        sum_resp = await client.get(sum_url, headers=headers)
                        snippet = ""
                        if sum_resp.status_code == 200:
                            snippet = sum_resp.json().get("extract", "")
                        if not snippet:
                            snippet = f"Wikipedia reference entry for {t}."
                        results.append(SearchResult(title=f"{t} (Wikipedia)", url=u, snippet=snippet))
                        if len(results) >= max_results:
                            break
        except Exception as e:
            logger.debug(f"Wikipedia search error for '{query}': {e}")
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
