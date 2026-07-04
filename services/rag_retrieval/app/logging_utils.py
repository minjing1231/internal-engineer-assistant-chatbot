from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from time import perf_counter
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import Response


def install_file_logging(app: FastAPI, service_name: str) -> None:
    logger = _build_logger(service_name)

    @app.on_event("startup")
    async def log_startup() -> None:
        _write(logger, {"event": "service_started", "service": service_name, "started_at": _now()})

    @app.middleware("http")
    async def log_payloads(request: Request, call_next):
        started = perf_counter()
        request_body = await request.body()
        request = Request(request.scope, _receive_once(request_body))
        response = await call_next(request)
        chunks = [chunk async for chunk in response.body_iterator]
        response_body = b"".join(chunks)
        _write(
            logger,
            {
                "event": "api_call",
                "service": service_name,
                "timestamp": _now(),
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
                "request_payload": _decode_payload(request_body, request.headers.get("content-type")),
                "response_payload": _decode_payload(response_body, response.headers.get("content-type")),
            },
        )
        headers = dict(response.headers)
        headers.pop("content-length", None)
        return Response(content=response_body, status_code=response.status_code, headers=headers, media_type=response.media_type)


def _build_logger(service_name: str) -> logging.Logger:
    log_file = Path(os.getenv("LOG_FILE", f"logs/{service_name}.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"payload.{service_name}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not any(isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file.resolve() for handler in logger.handlers):
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


def _write(logger: logging.Logger, payload: dict[str, Any]) -> None:
    logger.info(json.dumps(payload, ensure_ascii=True, default=str))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _receive_once(body: bytes):
    sent = False

    async def receive():
        nonlocal sent
        if sent:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    return receive


def _decode_payload(body: bytes, content_type: str | None) -> Any:
    if not body:
        return None
    text = body.decode("utf-8", errors="replace")
    if content_type and "application/json" in content_type:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return text
