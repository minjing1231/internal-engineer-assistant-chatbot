from .base import get_json, post_json


class LlmClient:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url
        self.timeout = timeout

    async def generate(
        self,
        question: str,
        sop_context: list[dict],
        structured_context: dict,
    ) -> dict:
        return await post_json(
            self.base_url,
            "/generate",
            {
                "question": question,
                "sop_context": sop_context,
                "structured_context": structured_context,
            },
            self.timeout,
        )

    async def health(self) -> dict:
        return await get_json(self.base_url, "/health", self.timeout)
