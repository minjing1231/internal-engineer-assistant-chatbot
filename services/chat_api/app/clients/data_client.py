from .base import get_json, post_json


class DataClient:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url
        self.timeout = timeout

    async def lookup(
        self,
        equipment: str | None,
        alarm_code: str | None,
        include_incidents: bool,
    ) -> dict:
        return await post_json(
            self.base_url,
            "/lookup",
            {
                "equipment": equipment,
                "alarm_code": alarm_code,
                "include_incidents": include_incidents,
                "incident_limit": 5,
            },
            self.timeout,
        )

    async def health(self) -> dict:
        return await get_json(self.base_url, "/health", self.timeout)
