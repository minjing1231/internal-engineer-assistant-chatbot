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

## Model Configuration

Copy `.env.example` to `.env` and configure your inference endpoint:

```text
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=LiquidAI/LFM2.5-1.2B-Instruct
```

## Current Status

The repository currently contains the assignment documents, SOP source, mock data, technical design, roadmap, and OpenAPI service contracts. Service implementation will follow the design in `document/TECHNICAL_DESIGN.md`.
