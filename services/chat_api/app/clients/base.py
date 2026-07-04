import httpx

from ..schemas import ServiceError


async def post_json(base_url: str, path: str, payload: dict, timeout: float) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{base_url}{path}", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise ServiceError(str(exc)) from exc


async def get_json(base_url: str, path: str, timeout: float) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{base_url}{path}")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise ServiceError(str(exc)) from exc
