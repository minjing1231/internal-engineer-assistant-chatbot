from .base import get_json, post_json


class RagClient:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url
        self.timeout = timeout

    async def search(
        self,
        query: str,
        equipment: str | None,
        alarm_code: str | None,
        top_k: int,
    ) -> dict:
        return await post_json(
            self.base_url,
            "/search",
            {
                "query": query,
                "equipment": equipment,
                "alarm_code": alarm_code,
                "top_k": top_k,
            },
            self.timeout,
        )

    async def health(self) -> dict:
        return await get_json(self.base_url, "/health", self.timeout)
