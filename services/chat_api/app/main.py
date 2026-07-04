from fastapi import FastAPI

from .clients.data_client import DataClient
from .clients.llm_client import LlmClient
from .clients.rag_client import RagClient
from .config import DATA_SERVICE_URL, LLM_SERVICE_URL, RAG_SERVICE_URL, SERVICE_TIMEOUT_SECONDS
from .orchestration.troubleshooting_flow import TroubleshootingFlow
from .schemas import ChatRequest, ChatResponse, HealthResponse, ServiceError

app = FastAPI(
    title="Chat API Service",
    version="0.1.0",
    description="Public orchestration API for the manufacturing repair assistant.",
)

data_client = DataClient(DATA_SERVICE_URL, SERVICE_TIMEOUT_SECONDS)
rag_client = RagClient(RAG_SERVICE_URL, SERVICE_TIMEOUT_SECONDS)
llm_client = LlmClient(LLM_SERVICE_URL, SERVICE_TIMEOUT_SECONDS)
flow = TroubleshootingFlow(data_client, rag_client, llm_client)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    dependencies = {}
    status = "ok"
    for name, client in {
        "mock_data": data_client,
        "rag_retrieval": rag_client,
        "llm_reasoning": llm_client,
    }.items():
        try:
            dependencies[name] = (await client.health()).get("status", "ok")
        except ServiceError:
            dependencies[name] = "error"
            status = "degraded"
    return HealthResponse(service="chat-api", status=status, dependencies=dependencies)


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    return await flow.answer(request)
