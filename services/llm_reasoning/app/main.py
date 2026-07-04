from fastapi import FastAPI

from .config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SECONDS,
)
from .logging_utils import install_file_logging
from .prompts.troubleshooting_prompt import build_messages
from .providers.openai_compatible_provider import LlmProviderError, generate_chat_completion
from .response_parser import fallback_answer, parse_answer
from .schemas import GenerateRequest, GenerateResponse, HealthResponse, Usage

app = FastAPI(
    title="LLM Reasoning Service",
    version="0.1.0",
    description="Prompt construction and LLM generation API for grounded troubleshooting responses.",
)
install_file_logging(app, "llm-reasoning")


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    configured = bool(LLM_BASE_URL)
    return HealthResponse(
        service="llm-reasoning",
        status="ok" if configured else "degraded",
        dependencies={
            "provider_configured": configured,
            "provider_type": "local_mlx",
            "model": LLM_MODEL,
        },
    )


@app.post("/generate", response_model=GenerateResponse, tags=["reasoning"])
async def generate(request: GenerateRequest) -> GenerateResponse:
    messages = build_messages(request)
    warnings: list[str] = []
    usage = None
    try:
        content, raw_usage = await generate_chat_completion(
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            model=LLM_MODEL,
            messages=messages,
            temperature=LLM_TEMPERATURE,
            timeout_seconds=LLM_TIMEOUT_SECONDS,
        )
        answer = parse_answer(content)
        if raw_usage:
            usage = Usage(
                input_tokens=raw_usage.get("prompt_tokens", 0),
                output_tokens=raw_usage.get("completion_tokens", 0),
            )
    except (LlmProviderError, ValueError) as exc:
        warnings.append(f"LLM fallback used: {exc}")
        answer = fallback_answer(request, uncertainty="LLM response unavailable or invalid.")

    return GenerateResponse(
        answer=answer,
        model=LLM_MODEL,
        usage=usage,
        warnings=warnings,
    )
