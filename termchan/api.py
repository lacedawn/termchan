import asyncio, time, logging
import httpx

from termchan.config import API_BASE, RATE_LIMIT, REQUEST_TIMEOUT, USER_AGENT
from termchan.models import Board, CatalogThread, Post

log = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, msg: str, status: int = 0):
        super().__init__(msg)
        self.status = status

class ThreadNotFound(APIError):
    pass


class _Limiter:
    """really basic rate limiter so we don't get banned"""
    def __init__(self):
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self):
        async with self._lock:
            gap = time.monotonic() - self._last
            if gap < RATE_LIMIT:
                await asyncio.sleep(RATE_LIMIT - gap)
            self._last = time.monotonic()


# module globals — fine for a single-process CLI app, would need
# rethinking if this ever became a library
_limiter = _Limiter()
_client: httpx.AsyncClient | None = None
_last_modified: dict[str, str] = {}    # url -> Last-Modified, for conditional requests
_cache_data: dict[str, dict | list] = {} # url -> JSON data


async def _ensure_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


async def _get(url: str, cache: bool = True) -> dict | list | None:
    await _limiter.wait()
    client = await _ensure_client()

    headers = {}
    if cache and url in _last_modified:
        headers["If-Modified-Since"] = _last_modified[url]

    try:
        r = await client.get(url, headers=headers)
    except httpx.TimeoutException:
        raise APIError(f"Timeout: {url}")
    except httpx.ConnectError:
        raise APIError(f"Connection failed: {url}")
    except httpx.HTTPError as e:
        raise APIError(str(e))

    if r.status_code == 304: 
        return _cache_data.get(url)  # return the cached json we saved earlier
    if r.status_code == 404:
        raise ThreadNotFound(f"Not found: {url}", status=404)
    if r.status_code != 200:
        raise APIError(f"HTTP {r.status_code}: {url}", status=r.status_code)

    data = r.json()
    if "Last-Modified" in r.headers:
        _last_modified[url] = r.headers["Last-Modified"]
        _cache_data[url] = data
    return data


async def fetch_boards() -> list[Board]:
    data = await _get(f"{API_BASE}/boards.json", cache=False)
    if not data: return []
    return [Board.from_json(b) for b in data.get("boards", [])]


async def fetch_catalog(board_name: str) -> list[CatalogThread]:
    data = await _get(f"{API_BASE}/{board_name}/catalog.json")
    if not data: return []
    out = []
    for page in data:
        for t in page.get("threads", []):
            out.append(CatalogThread.from_json(t))
    return out


async def fetch_thread(board_name: str, thread_no: int) -> list[Post]:
    data = await _get(f"{API_BASE}/{board_name}/thread/{thread_no}.json")
    if not data: return []
    return [Post.from_json(p) for p in data.get("posts", [])]


async def download(url: str) -> bytes:
    await _limiter.wait()
    client = await _ensure_client()
    try:
        r = await client.get(url)
        r.raise_for_status()
        return r.content
    except httpx.HTTPStatusError as e:
        raise APIError(f"Download failed ({e.response.status_code}): {url}")
    except httpx.HTTPError as e:
        raise APIError(f"Download failed: {e}")
