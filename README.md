# Manufacturing Equipment Repair Engineer Chatbot

This project is a take-home assignment for an agentic AI developer role. It designs a FastAPI microservice chatbot that helps manufacturing equipment repair engineers troubleshoot alarms using SOP retrieval, mock structured data, and an LLM reasoning service.

## Core Idea

The chatbot accepts a free-text troubleshooting question, retrieves relevant SOP context from `document/SOP.md`, enriches the request with equipment/alarm/incident data from `data/`, and generates a grounded response using:

```text
LiquidAI/LFM2.5-1.2B-Instruct
```

## Planned Services

| Service | Purpose |
| --- | --- |
| Chat API Service | User-facing orchestration service. |
| RAG Retrieval Service | Searches SOP content for relevant troubleshooting context. |
| LLM Reasoning Service | Builds prompts and calls the configured LiquidAI model. |
| Mock Data Service | Serves equipment, alarm, and historical incident CSV data. |

## Project Files

| Path | Description |
| --- | --- |
| `document/SOP.md` | Appendix A SOP knowledge source for RAG. |
| `data/*.csv` | Appendix B mock structured data. |
| `document/TECHNICAL_DESIGN.md` | High-level technical design and diagrams. |
| `document/ROADMAP.md` | 10-day delivery roadmap. |
| `document/API_CONTRACTS.md` | Human-readable API contract notes. |
| `openapi/*.openapi.yaml` | Real OpenAPI/Swagger specs for each service. |
| `.env.example` | Example environment configuration. |

## Run Locally

Create an environment file:

```bash
cp .env.example .env
```

Make sure your LiquidAI model is already running locally through MLX. If the MLX server is running on your Mac at port `8080`, keep this value in `.env` for Docker:

```text
LLM_BASE_URL=http://host.docker.internal:8080/v1
```

Then start the services:

```bash
docker compose up --build
```

Service docs:

| Service | Swagger URL |
| --- | --- |
| Chat API | `http://localhost:8000/docs` |
| RAG Retrieval | `http://localhost:8001/docs` |
| LLM Reasoning | `http://localhost:8002/docs` |
| Mock Data | `http://localhost:8003/docs` |

Minimal demo UI:

```text
http://localhost:8000/
```

Example chat request:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Etcher-03 triggered RF101 during plasma ignition. What should I check first?"}'
```

## Run Tests

```bash
pytest
```

## Service Logs

Each service writes JSON-lines logs under `logs/` when running through Docker Compose:

| Service | Log File |
| --- | --- |
| Chat API | `logs/chat-api.log` |
| RAG Retrieval | `logs/rag-retrieval.log` |
| LLM Reasoning | `logs/llm-reasoning.log` |
| Mock Data | `logs/mock-data.log` |

Each log file includes service startup time and API request/response payloads.

## Model Configuration

Copy `.env.example` to `.env` and configure your inference endpoint:

```text
LLM_BASE_URL=http://host.docker.internal:8080/v1
LLM_MODEL=LiquidAI/LFM2.5-1.2B-Instruct
LLM_API_KEY=
```

`LLM_API_KEY` is optional for local MLX. Leave it empty if your local model server does not require authentication.

## Current Status

The repository contains the assignment documents, SOP source, mock data, technical design, roadmap, OpenAPI service contracts, FastAPI service implementation, Dockerfiles, Docker Compose configuration, and unit tests.
