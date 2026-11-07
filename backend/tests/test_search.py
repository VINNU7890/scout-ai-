import asyncio

from backend.app.services.cache_service import CacheService
from backend.app.tools.search import (
    DuckDuckGoSearchProvider,
    SearchResult,
    get_search_provider,
    set_mock_search_provider,
)


def test_search_provider_interface():
    provider = get_search_provider()
    assert hasattr(provider, "search")


def test_search_caching():
    cache_key = "ddg:cached query:3"
    fake_results = [
        {"title": "Cached Title", "url": "https://example.com/cached", "snippet": "Snippet"}
    ]
    CacheService.set(cache_key, category="search", data=fake_results)

    provider = DuckDuckGoSearchProvider()
    results = asyncio.run(provider.search("cached query", max_results=3))

    assert len(results) == 1
    assert results[0].title == "Cached Title"
    assert results[0].url == "https://example.com/cached"


def test_mock_search_provider():
    class CustomSearchProvider:
        async def search(self, query: str, max_results: int = 5):
            return [
                SearchResult(title="Mock Title", url="https://mock.com", snippet="Mock snippet")
            ]

    set_mock_search_provider(CustomSearchProvider())
    try:
        prov = get_search_provider()
        res = asyncio.run(prov.search("test mock query", max_results=2))
        assert len(res) == 1
        assert res[0].title == "Mock Title"
    finally:
        set_mock_search_provider(None)
