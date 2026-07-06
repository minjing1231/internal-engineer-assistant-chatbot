# FastAPI Service API Contracts

This document defines the current API contracts between the chatbot microservices. Each service is implemented with FastAPI and exposes Swagger UI through `/docs`, ReDoc through `/redoc`, and raw OpenAPI through `/openapi.json`.

## 1. Swagger URLs

| Service | Base URL | Swagger UI | OpenAPI JSON |
| --- | --- | --- | --- |
| Chat API Service | `http://localhost:8000` | `http://localhost:8000/docs` | `http://localhost:8000/openapi.json` |
| RAG Retrieval Service | `http://localhost:8001` | `http://localhost:8001/docs` | `http://localhost:8001/openapi.json` |
| LLM Reasoning Service | `http://localhost:8002` | `http://localhost:8002/docs` | `http://localhost:8002/openapi.json` |
| Mock Data Service | `http://localhost:8003` | `http://localhost:8003/docs` | `http://localhost:8003/openapi.json` |

## 2. Shared API Conventions

- All service-to-service requests use JSON.
- All endpoints use Pydantic request/response models.
- Health endpoints are unauthenticated.
- Demo UI login is implemented in frontend JavaScript only and is not a production auth API.
- Docker Compose uses internal service URLs:
  - `http://rag-retrieval:8001`
  - `http://llm-reasoning:8002`
  - `http://mock-data:8003`
- Chat API waits up to `SERVICE_TIMEOUT_SECONDS=45` for service calls.
- LLM Reasoning waits up to `LLM_TIMEOUT_SECONDS=30` for the local MLX model provider.

## 3. Shared Schemas

### `HealthResponse`

```json
{
  "service": "chat-api",
  "status": "ok",
  "dependencies": {}
}
```

### `TroubleshootingAnswer`

Used by Chat API and LLM Reasoning.

```json
{
  "direct_response": null,
  "action_decision": {
    "primary_action": "Verify RF generator output reading from tool HMI.",
    "escalate": "Conditional",
    "reason": "Escalation depends on the listed SOP criteria."
  },
  "issue_summary": {
    "equipment": "Etcher-03",
    "alarm_or_symptom": "RF101",
    "severity": "High"
  },
  "relevant_sop_context": [
    {
      "source_id": "SOP-ETCH-001",
      "title": "Etcher RF Power Instability - Alarm RF101",
      "section": "Troubleshooting Steps"
    }
  ],
  "recommended_checks": [
    "Verify RF generator output reading from tool HMI."
  ],
  "likely_causes": [
    "RF generator drift"
  ],
  "recovery_next_steps": [
    "Restart RF subsystem only if permitted by local operating procedure."
  ],
  "safety_precautions": [
    "Confirm tool is in safe state before opening panels."
  ],
  "escalation_criteria": [
    "RF101 repeats more than twice within 7 days."
  ],
  "uncertainty": []
}
```

Field notes:

| Field | Type | Description |
| --- | --- | --- |
| `direct_response` | string or null | Short FE response for correction cases, for example `Cannot find alarm type GAS0. Do you mean GAS012?`. If present, FE formatting uses this directly. |
| `action_decision.escalate` | string | One of `Yes`, `No`, `Conditional`, or `Unknown`. |
| `issue_summary.severity` | string or null | One of `Low`, `Medium`, `High`, or null. |
| list fields | array | Always arrays, even when one item exists. |

## 4. Chat API Service

FastAPI title: `Chat API Service`

Base URLs:

- Local host: `http://localhost:8000`
- Docker network: `http://chat-api:8000`

### `GET /`

Serves the browser frontend.

Current UI behavior:

- Demo login page.
- Hardcoded demo credentials in frontend JavaScript: `hana` / `123`.
- Assistant-only chat session after login.
- Sample questions hidden behind a toggle.
- `Enter` submits; `Shift + Enter` inserts a new line.

### `POST /api/chat`

Frontend endpoint used by the browser UI.

Request schema: `ApiChatRequest`

```json
{
  "message": "CVD-05 triggered GAS012 during deposition. Should I escalate?",
  "configuration": "all",
  "region": "SOP-CVD-003"
}
```

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `message` | string | yes | User question. |
| `configuration` | string or null | no | Kept for UI compatibility; current assistant-only UI sends `all`. |
| `region` | string or null | no | Kept for UI compatibility. |

Response schema: `ApiChatResponse`

```json
{
  "answer": "Action Decision:\n- Primary Action: Escalate and verify gas flow deviation conditions.\n- Escalate: Yes\n- Reason: GAS012 is a high-severity gas flow deviation alarm.",
  "model_name": "LiquidAI/LFM2.5-1.2B-Instruct",
  "retrieval_count": 3,
  "generated": true,
  "state_references": [],
  "warnings": []
}
```

Notes:

- `answer` is already formatted for the frontend.
- `state_references` may be returned by backend, but SOP jump-chip rendering is currently commented out in the UI.
- For typo/mismatch cases, `answer` is a direct correction string such as `Cannot find equipment ID Etcher-0399. Do you mean Etcher-03?`.
- `generated=false` means fallback or warning path was used.

### `POST /chat`

Structured API endpoint used for testing or direct API integration.

Request schema: `ChatRequest`

```json
{
  "question": "Etcher-03 triggered RF101 during plasma ignition. What should I check first?",
  "top_k": 4,
  "include_incidents": true
}
```

Response schema: `ChatResponse`

```json
{
  "answer": {
    "direct_response": null,
    "action_decision": {
      "primary_action": "Verify RF generator output reading from tool HMI.",
      "escalate": "Conditional",
      "reason": "Escalation depends on whether RF101 persists, repeats, or hardware fault is suspected."
    },
    "issue_summary": {
      "equipment": "Etcher-03",
      "alarm_or_symptom": "RF101",
      "severity": "High"
    },
    "relevant_sop_context": [],
    "recommended_checks": [],
    "likely_causes": [],
    "recovery_next_steps": [],
    "safety_precautions": [],
    "escalation_criteria": [],
    "uncertainty": []
  },
  "sources": [
    {
      "type": "sop",
      "id": "SOP-ETCH-001",
      "section": "Troubleshooting Steps"
    }
  ],
  "warnings": []
}
```

Important Chat API behavior:

- Extracts equipment IDs like `Etcher-03` and `Etcher-0399`.
- Extracts alarm codes like `RF101`, `GAS012`, and typo-like codes such as `GAS0`.
- Calls Mock Data, RAG Retrieval, then LLM Reasoning if context is confirmed.
- Blocks unconfirmed ID mismatches before LLM generation.
- Uses deterministic fallback if LLM Reasoning is unavailable.

### `GET /health`

Returns dependency status for RAG Retrieval, LLM Reasoning, and Mock Data.

## 5. RAG Retrieval Service

FastAPI title: `RAG Retrieval Service`

Base URLs:

- Local host: `http://localhost:8001`
- Docker network: `http://rag-retrieval:8001`

### `POST /search`

Searches indexed SOP chunks using keyword overlap plus metadata boosts.

Request schema: `SearchRequest`

```json
{
  "query": "Etcher-03 has RF101 alarm during plasma ignition",
  "equipment": "Etcher-03",
  "alarm_code": "RF101",
  "top_k": 4
}
```

Response schema: `SearchResponse`

```json
{
  "results": [
    {
      "chunk_id": "SOP-ETCH-001:troubleshooting-steps",
      "source_id": "SOP-ETCH-001",
      "title": "Etcher RF Power Instability - Alarm RF101",
      "section": "Troubleshooting Steps",
      "equipment": ["Plasma Etcher", "Etcher-03"],
      "alarm_code": "RF101",
      "severity": "High",
      "content": "1. Verify RF generator output reading from tool HMI.",
      "score": 12.5
    }
  ]
}
```

Retrieval scoring:

- Keyword overlap over source ID, title, section, equipment, alarm code, severity, and content.
- Exact alarm match boost: `+8.0`.
- Exact equipment match boost: `+4.0`.
- Section boost: `+0.25` for safety, troubleshooting, and escalation sections.

### `POST /reindex`

Reloads `document/SOP.md` and rebuilds the in-memory index.

### `GET /health`

Returns SOP load status and indexed chunk count.

## 6. LLM Reasoning Service

FastAPI title: `LLM Reasoning Service`

Base URLs:

- Local host: `http://localhost:8002`
- Docker network: `http://llm-reasoning:8002`

### `POST /generate`

Builds a grounded prompt, calls the local MLX model endpoint, parses model JSON, and normalizes the structured answer.

Request schema: `GenerateRequest`

```json
{
  "question": "CVD-05 triggered GAS012 during deposition. Should I escalate?",
  "sop_context": [
    {
      "chunk_id": "SOP-CVD-003:escalation-criteria",
      "source_id": "SOP-CVD-003",
      "title": "CVD Gas Flow Deviation - Alarm GAS012",
      "section": "Escalation Criteria",
      "content": "- Any gas safety concern exists.",
      "score": 13.0
    }
  ],
  "structured_context": {
    "equipment": {
      "equipment_id": "EQ003",
      "equipment_name": "CVD-05",
      "tool_type": "PECVD Tool",
      "area": "Deposition",
      "status": "Active"
    },
    "alarm": {
      "alarm_code": "GAS012",
      "description": "Gas Flow Deviation",
      "severity": "High"
    },
    "incidents": []
  }
}
```

Response schema: `GenerateResponse`

```json
{
  "answer": {
    "direct_response": null,
    "action_decision": {
      "primary_action": "Escalate and verify gas flow deviation conditions.",
      "escalate": "Yes",
      "reason": "GAS012 is high severity and gas-related alarms are high priority."
    },
    "issue_summary": {
      "equipment": "CVD-05",
      "alarm_or_symptom": "GAS012",
      "severity": "High"
    },
    "relevant_sop_context": [],
    "recommended_checks": [],
    "likely_causes": [],
    "recovery_next_steps": [],
    "safety_precautions": [],
    "escalation_criteria": [],
    "uncertainty": []
  },
  "model": "LiquidAI/LFM2.5-1.2B-Instruct",
  "usage": {
    "input_tokens": 676,
    "output_tokens": 304
  },
  "warnings": []
}
```

LLM logging:

- `llm_provider_request` logs model settings and messages.
- `llm_provider_response` logs raw model content and usage.
- `llm_provider_error` logs provider or parse errors.
- `LLM_API_KEY` is not logged.

### `GET /health`

Returns provider configuration status and model name.

## 7. Mock Data Service

FastAPI title: `Mock Data Service`

Base URLs:

- Local host: `http://localhost:8003`
- Docker network: `http://mock-data:8003`

### `GET /equipment/{equipment_name}`

Looks up one equipment record.

### `GET /alarms/{alarm_code}`

Looks up one alarm record.

### `GET /incidents`

Query parameters:

| Parameter | Type | Required | Default |
| --- | --- | --- | --- |
| `equipment` | string | no | `null` |
| `alarm_code` | string | no | `null` |
| `limit` | integer | no | `5` |

### `POST /lookup`

Combined lookup endpoint used by Chat API.

Request schema: `LookupRequest`

```json
{
  "equipment": "Etcher-03",
  "alarm_code": "RF101",
  "include_incidents": true,
  "incident_limit": 5
}
```

Response schema: `LookupResponse`

```json
{
  "equipment": {
    "equipment_id": "EQ001",
    "equipment_name": "Etcher-03",
    "tool_type": "Plasma Etcher",
    "area": "Etch",
    "status": "Active"
  },
  "alarm": {
    "alarm_code": "RF101",
    "description": "RF Power Instability",
    "severity": "High"
  },
  "incidents": [],
  "missing": []
}
```

The `missing` array can include `equipment`, `alarm`, or `incidents`.

### `GET /health`

Returns equipment, alarm, and incident record counts.

## 8. Operational Notes

- Local MLX model URL defaults to `http://host.docker.internal:8080/v1` in Docker.
- Chat API timeout should be greater than LLM Reasoning model timeout.
- Logs are written under `logs/` when using Docker Compose.
- Direct frontend users should open `http://localhost:8000/`.
- API testers can use `http://localhost:8000/chat` for structured responses or `http://localhost:8000/api/chat` for FE-formatted responses.
