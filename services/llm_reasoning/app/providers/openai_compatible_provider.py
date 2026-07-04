import httpx


class LlmProviderError(RuntimeError):
    pass


async def generate_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    timeout_seconds: float,
) -> tuple[str, dict[str, int] | None]:
    if not base_url:
        raise LlmProviderError("LLM_BASE_URL is not configured")

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LlmProviderError(str(exc)) from exc

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmProviderError("Provider response did not include message content") from exc
    return content, data.get("usage")
