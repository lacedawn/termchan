from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from termchan.api import (
    APIError, ThreadNotFound, _Limiter,
    fetch_boards, fetch_catalog, fetch_thread, download,
)


def _fake_response(body, status=200, headers=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = body
    r.headers = headers or {}
    r.content = b"imagedata"
    r.raise_for_status = MagicMock()
    return r


def _patched_client(response):
    """helper: patches _ensure_client to return a mock with the given response"""
    client = AsyncMock()
    client.get = AsyncMock(return_value=response)
    return patch("termchan.api._ensure_client", new_callable=AsyncMock, return_value=client)


@pytest.fixture(autouse=True)
def reset_limiter():
    """skip rate limiting in tests"""
    import termchan.api as api
    api._limiter._last = 0


class TestLimiter:
    @pytest.mark.asyncio
    async def test_no_delay_on_first_call(self):
        import time
        lim = _Limiter()
        t0 = time.monotonic()
        await lim.wait()
        assert time.monotonic() - t0 < 0.1

    @pytest.mark.asyncio
    async def test_delays_subsequent_calls(self):
        import time
        lim = _Limiter()
        lim._last = time.monotonic()       # pretend we just made a request
        t0 = time.monotonic()
        await lim.wait()
        assert time.monotonic() - t0 >= 0.9


class TestFetching:
    @pytest.mark.asyncio
    async def test_boards(self):
        data = {"boards": [{"board": "g", "title": "Tech", "ws_board": 1}]}
        with _patched_client(_fake_response(data)):
            boards = await fetch_boards()
        assert len(boards) == 1
        assert boards[0].board == "g"

    @pytest.mark.asyncio
    async def test_catalog(self):
        data = [{"page": 1, "threads": [{"no": 100, "sub": "T", "replies": 5}]}]
        with _patched_client(_fake_response(data)):
            threads = await fetch_catalog("g")
        assert len(threads) == 1
        assert threads[0].no == 100

    @pytest.mark.asyncio
    async def test_thread_posts(self):
        data = {"posts": [{"no": 1, "com": "hi", "resto": 0}]}
        with _patched_client(_fake_response(data)):
            posts = await fetch_thread("g", 1)
        assert len(posts) == 1
        assert posts[0].com == "hi"

    @pytest.mark.asyncio
    async def test_404_raises(self):
        with _patched_client(_fake_response(None, 404)):
            with pytest.raises(ThreadNotFound):
                await fetch_thread("g", 99999)

    @pytest.mark.asyncio
    async def test_304_returns_empty(self):
        with _patched_client(_fake_response(None, 304)):
            result = await fetch_catalog("g")
        assert result == []

    @pytest.mark.asyncio
    async def test_download_bytes(self):
        with _patched_client(_fake_response(None)):
            data = await download("https://i.4cdn.org/g/12345.jpg")
        assert data == b"imagedata"
