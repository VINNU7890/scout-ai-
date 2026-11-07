from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from backend.app.config import get_settings
from backend.app.services.cache_service import CacheService
from backend.app.utils.url_safety import validate_url

logger = logging.getLogger("scoutai.tools.fetch")
settings = get_settings()

USER_AGENT = "ScoutAI-ResearchBot/1.0 (+https://github.com/scoutai; research-agent)"


class FetchedPage(BaseModel):
    url: str
    title: str
    content: str
    success: bool
    error: Optional[str] = None


async def can_fetch_robots(url: str, client: httpx.AsyncClient) -> bool:
    """Best-effort robots.txt check."""
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        validate_url(robots_url)
        resp = await client.get(robots_url, headers={"User-Agent": USER_AGENT}, timeout=3.0)
        if resp.status_code == 200:
            lines = resp.text.splitlines()
            current_applies = False
            for line in lines:
                line_clean = line.strip().lower()
                if line_clean.startswith("user-agent:"):
                    ua = line_clean.split(":", 1)[1].strip()
                    current_applies = ua == "*" or "scoutai" in ua
                elif line_clean.startswith("disallow:") and current_applies:
                    path = line_clean.split(":", 1)[1].strip()
                    if path == "/" or (path and parsed.path.startswith(path)):
                        return False
    except Exception:
        # If robots.txt check fails or times out, proceed permissively
        pass
    return True


async def fetch_and_clean_page(
    url: str,
    client: Optional[httpx.AsyncClient] = None,
) -> FetchedPage:
    """
    Fetches a web page with SSRF protection, size caps, robots.txt check,
    cleans HTML to text via trafilatura/BeautifulSoup, truncates, and caches result.
    """
    cache_key = f"fetch:{url.strip()}"
    cached = CacheService.get(cache_key, category="fetch")
    if cached and isinstance(cached, dict):
        logger.info(f"Returning cached page fetch for: {url}")
        return FetchedPage(**cached)

    try:
        validate_url(url)
    except Exception as e:
        logger.warning(f"SSRF validation blocked {url}: {e}")
        return FetchedPage(url=url, title="", content="", success=False, error=str(e))

    close_client = False
    if client is None:
        client = httpx.AsyncClient(
            timeout=settings.FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        close_client = True

    try:
        # Check robots.txt
        allowed = await can_fetch_robots(url, client)
        if not allowed:
            logger.info(f"Skipping {url} due to robots.txt Disallow")
            return FetchedPage(
                url=url,
                title="",
                content="",
                success=False,
                error="Disallowed by robots.txt",
            )

        # Stream response to enforce 1.5MB size cap safely
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}
        async with client.stream("GET", url, headers=headers) as response:
            if response.status_code >= 400:
                return FetchedPage(
                    url=url,
                    title="",
                    content="",
                    success=False,
                    error=f"HTTP {response.status_code}",
                )

            content_bytes = bytearray()
            async for chunk in response.aiter_bytes():
                content_bytes.extend(chunk)
                if len(content_bytes) > settings.MAX_FETCH_SIZE_BYTES:
                    logger.warning(
                        f"Page exceeded {settings.MAX_FETCH_SIZE_BYTES} bytes cap: {url}"
                    )
                    break

        html_text = content_bytes.decode("utf-8", errors="replace")

        # Clean HTML using trafilatura with beautifulsoup fallback
        extracted_text = ""
        title = ""

        try:
            import trafilatura

            extracted_text = (
                trafilatura.extract(
                    html_text,
                    include_comments=False,
                    include_tables=True,
                    no_fallback=False,
                )
                or ""
            )
            metadata = trafilatura.extract_metadata(html_text)
            if metadata and metadata.title:
                title = metadata.title
        except Exception as e:
            logger.debug(f"Trafilatura error on {url}, falling back to BeautifulSoup: {e}")

        if not extracted_text:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_text, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            if not title and soup.title and soup.title.string:
                title = soup.title.string.strip()
            extracted_text = soup.get_text(separator="\n", strip=True)

        if not title:
            parsed = urlparse(url)
            title = parsed.netloc

        # Enforce token/char length guard
        if len(extracted_text) > settings.PAGE_TRUNCATION_LIMIT:
            extracted_text = extracted_text[: settings.PAGE_TRUNCATION_LIMIT] + "\n...[truncated]"

        result = FetchedPage(
            url=url,
            title=title.strip(),
            content=extracted_text.strip(),
            success=True,
        )

        CacheService.set(cache_key, category="fetch", data=result.model_dump())
        return result

    except Exception as e:
        logger.warning(f"Error fetching page {url}: {e}")
        return FetchedPage(url=url, title="", content="", success=False, error=str(e))
    finally:
        if close_client:
            await client.aclose()
