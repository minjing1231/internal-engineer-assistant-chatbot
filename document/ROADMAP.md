# 10-Day Delivery Roadmap

## Purpose

This roadmap explains how the take-home assignment will be delivered within the recommended 10-day duration. The plan prioritizes a working microservice demo first, then improves reliability, documentation, and presentation quality before submission.

## Delivery Plan

| Day | Focus | Planned Output |
| --- | --- | --- |
| Day 1 | Design and project structure | Finalize technical design, service boundaries, repository structure, SOP/data files, environment variables, and OpenAPI contracts. |
| Day 2 | Core service development | Build FastAPI skeletons for Chat API, RAG Retrieval, LLM Reasoning, and Mock Data services. Add health checks and shared schemas. |
| Day 3 | Feature development | Implement CSV data lookup, SOP ingestion/chunking, retrieval ranking, orchestration flow, and LLM provider integration using `LiquidAI/LFM2.5-1.2B-Instruct`. |
| Day 4 | End-to-end behavior | Connect all services through Docker Compose. Implement graceful handling for unknown equipment, unknown alarms, missing SOP context, and LLM failures. |
| Day 5 | Unit testing | Add unit tests for SOP parsing, retrieval ranking, CSV loading, data lookup, prompt construction, and response formatting. |
| Day 6 | Integration testing | Run full workflow tests across services using the required example questions. Verify source references, uncertainty handling, and fallback behavior. |
| Day 7 | RAG and response tuning | Tune retrieval scoring, prompt wording, answer structure, and safety/escalation behavior based on test results. |
| Day 8 | Documentation polish | Update README, technical design, API/Swagger docs, setup instructions, known limitations, and example questions with sample outputs. |
| Day 9 | Demo preparation | Prepare a 5-10 minute demo script, rehearse the walkthrough, verify clean local setup, and record the demo video. |
| Day 10 | Final review and submission | Run final smoke tests, review repository cleanliness, confirm environment examples, upload video, and submit the GitHub repository link. |

## Milestones

| Milestone | Target Day | Success Criteria |
| --- | --- | --- |
| Design ready | Day 1 | Service responsibilities, data sources, and model choice are clearly documented. |
| Services runnable | Day 3 | Each FastAPI service starts independently and exposes Swagger docs. |
| End-to-end demo working | Day 4 | A user question can flow from Chat API through retrieval, data lookup, LLM reasoning, and final response. |
| Tests passing | Day 6 | Unit and integration tests cover known alarms, unknown alarms, and failure paths. |
| Submission ready | Day 10 | README, docs, video demo, and repository are ready for reviewer access. |

## Demo Readiness Checklist

- All services run through Docker Compose.
- Swagger docs are available for every FastAPI service.
- `document/SOP.md` is used as the RAG knowledge source.
- `data/*.csv` files are used as structured mock data.
- The chatbot uses `LiquidAI/LFM2.5-1.2B-Instruct` for reasoning.
- At least five assignment test questions are verified.
- Unknown alarm and insufficient-information cases are handled gracefully.
- Final answers include SOP references and uncertainty notes.

## Risk Buffer

The plan intentionally leaves Days 7-10 for tuning, documentation, demo rehearsal, and final review. This buffer is important because LLM/RAG behavior often needs iteration after the first end-to-end version works.

Primary risks:

- Model endpoint setup may take longer than expected.
- Retrieval may need tuning for alarm-code-heavy questions.
- LLM responses may need prompt adjustments to stay structured and grounded.
- Docker Compose or environment setup may need cleanup for reviewer usability.
