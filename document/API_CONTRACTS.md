# FastAPI Service API Contracts

This document defines the API contracts between the chatbot microservices. Each service should be implemented with FastAPI and expose Swagger UI automatically through `/docs`, ReDoc through `/redoc`, and the raw OpenAPI document through `/openapi.json`.

## 1. Swagger URLs

When running locally with Docker Compose:

| Service | Base URL | Swagger UI | OpenAPI JSON |
| --- | --- | --- | --- |
| Chat API Service | `http://localhost:8000` | `http://localhost:8000/docs` | `http://localhost:8000/openapi.json` |
| RAG Retrieval Service | `http://localhost:8001` | `http://localhost:8001/docs` | `http://localhost:8001/openapi.json` |
| LLM Reasoning Service | `http://localhost:8002` | `http://localhost:8002/docs` | `http://localhost:8002/openapi.json` |
| Mock Data Service | `http://localhost:8003` | `http://localhost:8003/docs` | `http://localhost:8003/openapi.json` |

Recommended FastAPI metadata:

```python
app = FastAPI(
    title="Chat API Service",
    version="0.1.0",
    description="Public orchestration API for the manufacturing repair assistant.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

## 2. Shared API Conventions

- All services use JSON request and response bodies.
- All timestamps and dates use ISO-8601 strings.
- All service-to-service calls use short timeouts.
- All endpoints expose Pydantic response models so Swagger documents the exact schema.
- Health endpoints are unauthenticated.
- Local demo authentication is out of scope.

### Standard Error Response

Use this response body for `400`, `404`, `422`, `500`, and `503` responses where possible.

```json
{
  "error_code": "unknown_alarm",
  "message": "Alarm code ABC999 was not found in the mock alarm reference.",
  "details": {
    "alarm_code": "ABC999"
  }
}
```

Schema:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `error_code` | string | yes | Stable machine-readable error code. |
| `message` | string | yes | Human-readable explanation. |
| `details` | object | no | Optional context about the failure. |

### Standard Health Response

```json
{
  "service": "rag-retrieval",
  "status": "ok",
  "dependencies": {
    "sop_loaded": true
  }
}
```

Schema:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `service` | string | yes | Service name. |
| `status` | string | yes | `ok`, `degraded`, or `error`. |
| `dependencies` | object | no | Service-specific dependency details. |

## 3. Chat API Service

FastAPI title: `Chat API Service`

Base URL:

- Local host: `http://localhost:8000`
- Docker network: `http://chat-api:8000`

Tags:

- `chat`
- `health`

### `POST /chat`

Public endpoint used by the demo user or UI. This endpoint orchestrates calls to the Mock Data, RAG Retrieval, and LLM Reasoning services.

Request schema: `ChatRequest`

```json
{
  "question": "Etcher-03 triggered RF101 during plasma ignition. What should I check first?",
  "top_k": 4,
  "include_incidents": true
}
```

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `question` | string | yes | none | Free-text troubleshooting question. |
| `top_k` | integer | no | `4` | Number of SOP chunks to request from RAG service. |
| `include_incidents` | boolean | no | `true` | Whether to request historical incidents from Mock Data Service. |

Response schema: `ChatResponse`

```json
{
  "answer": {
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
      "Verify RF generator output reading from tool HMI.",
      "Check recent RF power trend for sudden drop or oscillation."
    ],
    "safety_precautions": [
      "Confirm tool is in safe state before opening panels."
    ],
    "escalation_criteria": [
      "Escalate if RF101 repeats more than twice within 7 days."
    ],
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

Status codes:

| Code | Meaning |
| --- | --- |
| `200` | Answer generated or deterministic fallback returned. |
| `400` | Empty or invalid question. |
| `503` | Required RAG service unavailable. |

### `GET /health`

Response schema: `HealthResponse`

```json
{
  "service": "chat-api",
  "status": "ok",
  "dependencies": {
    "rag_retrieval": "ok",
    "llm_reasoning": "ok",
    "mock_data": "ok"
  }
}
```

## 4. RAG Retrieval Service

FastAPI title: `RAG Retrieval Service`

Base URL:

- Local host: `http://localhost:8001`
- Docker network: `http://rag-retrieval:8001`

Tags:

- `retrieval`
- `index`
- `health`

### `POST /search`

Searches indexed SOP chunks and returns relevant context with citation metadata.

Request schema: `SearchRequest`

```json
{
  "query": "Etcher-03 has RF101 alarm during plasma ignition",
  "equipment": "Etcher-03",
  "alarm_code": "RF101",
  "top_k": 4
}
```

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `query` | string | yes | none | Original user question or search text. |
| `equipment` | string | no | `null` | Extracted equipment name. |
| `alarm_code` | string | no | `null` | Extracted alarm code. |
| `top_k` | integer | no | `4` | Maximum chunks to return. |

Response schema: `SearchResponse`

```json
{
  "results": [
    {
      "chunk_id": "SOP-ETCH-001:troubleshooting",
      "source_id": "SOP-ETCH-001",
      "title": "Etcher RF Power Instability - Alarm RF101",
      "section": "Troubleshooting Steps",
      "equipment": ["Plasma Etcher", "Etcher-03"],
      "alarm_code": "RF101",
      "severity": "High",
      "content": "Verify RF generator output reading from tool HMI...",
      "score": 0.92
    }
  ]
}
```

Status codes:

| Code | Meaning |
| --- | --- |
| `200` | Search completed. Results may be empty. |
| `400` | Invalid query or `top_k`. |
| `503` | SOP index is unavailable. |

### `POST /reindex`

Reloads `document/SOP.md` and rebuilds the in-memory index. This is helpful for a local demo.

Request schema: none.

Response schema: `ReindexResponse`

```json
{
  "status": "ok",
  "sop_path": "/app/document/SOP.md",
  "chunks_indexed": 40
}
```

### `GET /health`

Response schema: `HealthResponse`

```json
{
  "service": "rag-retrieval",
  "status": "ok",
  "dependencies": {
    "sop_loaded": true,
    "chunks_indexed": 40
  }
}
```

## 5. LLM Reasoning Service

FastAPI title: `LLM Reasoning Service`

Base URL:

- Local host: `http://localhost:8002`
- Docker network: `http://llm-reasoning:8002`

Tags:

- `reasoning`
- `health`

### `POST /generate`

Builds a grounded prompt from the question, SOP context, and structured mock data. Calls the configured LLM provider and returns a structured troubleshooting answer.

Request schema: `GenerateRequest`

```json
{
  "question": "CVD-05 triggered GAS012 during deposition. Should I escalate?",
  "sop_context": [
    {
      "chunk_id": "SOP-CVD-003:escalation",
      "source_id": "SOP-CVD-003",
      "title": "CVD Gas Flow Deviation - Alarm GAS012",
      "section": "Escalation Criteria",
      "content": "Any gas safety concern exists. Downtime exceeds 20 minutes for high-severity gas alarm.",
      "score": 0.95
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
    "issue_summary": {
      "equipment": "CVD-05",
      "alarm_or_symptom": "GAS012",
      "severity": "High"
    },
    "relevant_sop_context": [
      {
        "source_id": "SOP-CVD-003",
        "title": "CVD Gas Flow Deviation - Alarm GAS012",
        "section": "Escalation Criteria"
      }
    ],
    "recommended_checks": [
      "Compare MFC actual reading with recipe target.",
      "Check gas supply pressure and facility gas status."
    ],
    "safety_precautions": [
      "Treat gas-related alarms as high priority.",
      "Do not bypass gas interlocks."
    ],
    "escalation_criteria": [
      "Escalate if any gas safety concern exists.",
      "Escalate if MFC drift or leak is suspected."
    ],
    "uncertainty": []
  },
  "model": "LiquidAI/LFM2.5-1.2B-Instruct",
  "usage": {
    "input_tokens": 1200,
    "output_tokens": 350
  },
  "warnings": []
}
```

Status codes:

| Code | Meaning |
| --- | --- |
| `200` | LLM answer generated and parsed. |
| `400` | Missing question or missing SOP context. |
| `503` | LLM provider unavailable or timed out. |

### `GET /health`

Response schema: `HealthResponse`

```json
{
  "service": "llm-reasoning",
  "status": "ok",
  "dependencies": {
    "provider_configured": true,
    "provider_type": "local_mlx",
    "model": "LiquidAI/LFM2.5-1.2B-Instruct"
  }
}
```

The local MLX endpoint should be reported as configured, but secrets should not be exposed in this response.

## 6. Mock Data Service

FastAPI title: `Mock Data Service`

Base URL:

- Local host: `http://localhost:8003`
- Docker network: `http://mock-data:8003`

Tags:

- `equipment`
- `alarms`
- `incidents`
- `lookup`
- `health`

### `GET /equipment/{equipment_name}`

Looks up equipment by display name.

Example:

```text
GET /equipment/Etcher-03
```

Response schema: `Equipment`

```json
{
  "equipment_id": "EQ001",
  "equipment_name": "Etcher-03",
  "tool_type": "Plasma Etcher",
  "area": "Etch",
  "status": "Active"
}
```

Status codes:

| Code | Meaning |
| --- | --- |
| `200` | Equipment found. |
| `404` | Equipment not found. |

### `GET /alarms/{alarm_code}`

Looks up an alarm by alarm code.

Example:

```text
GET /alarms/RF101
```

Response schema: `Alarm`

```json
{
  "alarm_code": "RF101",
  "description": "RF Power Instability",
  "severity": "High"
}
```

Status codes:

| Code | Meaning |
| --- | --- |
| `200` | Alarm found. |
| `404` | Alarm not found. |

### `GET /incidents`

Finds historical incidents by optional query filters.

Query parameters:

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `equipment` | string | no | `null` | Equipment name filter. |
| `alarm_code` | string | no | `null` | Alarm code filter. |
| `limit` | integer | no | `5` | Maximum incidents to return. |

Example:

```text
GET /incidents?equipment=Etcher-03&alarm_code=RF101&limit=5
```

Response schema: `IncidentList`

```json
{
  "incidents": [
    {
      "incident_id": "H001",
      "date": "2026-06-01",
      "equipment": "Etcher-03",
      "alarm_code": "RF101",
      "root_cause": "Loose RF cable",
      "corrective_action": "Tightened RF connector and verified reflected power"
    }
  ]
}
```

### `POST /lookup`

Combined lookup endpoint used by Chat API to reduce service-to-service round trips.

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
  "incidents": [
    {
      "incident_id": "H001",
      "date": "2026-06-01",
      "equipment": "Etcher-03",
      "alarm_code": "RF101",
      "root_cause": "Loose RF cable",
      "corrective_action": "Tightened RF connector and verified reflected power"
    }
  ],
  "missing": []
}
```

The `missing` array can contain `equipment`, `alarm`, or `incidents`.

Status codes:

| Code | Meaning |
| --- | --- |
| `200` | Lookup completed. Missing records are reported in the body. |
| `400` | Neither equipment nor alarm code was provided. |

### `GET /health`

Response schema: `HealthResponse`

```json
{
  "service": "mock-data",
  "status": "ok",
  "dependencies": {
    "equipment_records": 5,
    "alarm_records": 8,
    "incident_records": 6
  }
}
```

## 7. Shared Schema Names

Use these shared model names across services where possible to keep Swagger readable:

| Schema | Used By | Purpose |
| --- | --- | --- |
| `HealthResponse` | All services | Health and dependency status. |
| `ErrorResponse` | All services | Consistent error shape. |
| `SourceReference` | Chat API, LLM Reasoning | SOP/data citation. |
| `SopContextChunk` | RAG Retrieval, LLM Reasoning | Retrieved SOP chunk. |
| `Equipment` | Mock Data, LLM Reasoning | Equipment master record. |
| `Alarm` | Mock Data, LLM Reasoning | Alarm reference record. |
| `Incident` | Mock Data, LLM Reasoning | Historical incident record. |
| `TroubleshootingAnswer` | Chat API, LLM Reasoning | Structured chatbot answer. |

## 8. FastAPI Implementation Pattern

Each endpoint should include `response_model`, `summary`, `description`, and `tags` so Swagger is useful during the interview demo.

```python
@router.post(
    "/search",
    response_model=SearchResponse,
    tags=["retrieval"],
    summary="Search SOP context",
    description="Returns the most relevant SOP chunks for a troubleshooting question.",
)
async def search(request: SearchRequest) -> SearchResponse:
    ...
```

Service clients should call internal Docker network URLs:

```text
http://rag-retrieval:8001/search
http://llm-reasoning:8002/generate
http://mock-data:8003/lookup
```

The public demo should only need to call:

```text
http://localhost:8000/chat
```
