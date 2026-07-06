import httpx

from ..schemas import ServiceError


async def post_json(base_url: str, path: str, payload: dict, timeout: float) -> dict:
    url = f"{base_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise ServiceError(_describe_http_error(exc, url)) from exc


async def get_json(base_url: str, path: str, timeout: float) -> dict:
    url = f"{base_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise ServiceError(_describe_http_error(exc, url)) from exc


def _describe_http_error(exc: httpx.HTTPError, url: str) -> str:
    detail = str(exc).strip()
    if isinstance(exc, httpx.HTTPStatusError):
        return f"{type(exc).__name__} from {url}: HTTP {exc.response.status_code} {exc.response.text}"
    if detail:
        return f"{type(exc).__name__} from {url}: {detail}"
    return f"{type(exc).__name__} from {url}"
