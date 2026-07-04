from fastapi import FastAPI, HTTPException

from .config import DEFAULT_TOP_K, SOP_FILE_PATH
from .ingestion.markdown_loader import load_sop_chunks
from .retrieval.keyword_search import KeywordRetriever
from .schemas import HealthResponse, ReindexResponse, SearchRequest, SearchResponse

app = FastAPI(
    title="RAG Retrieval Service",
    version="0.1.0",
    description="SOP ingestion and retrieval API for the manufacturing repair assistant.",
)

chunks = load_sop_chunks(SOP_FILE_PATH)
retriever = KeywordRetriever(chunks)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(
        service="rag-retrieval",
        status="ok" if chunks else "degraded",
        dependencies={
            "sop_path": str(SOP_FILE_PATH),
            "sop_loaded": bool(chunks),
            "chunks_indexed": len(chunks),
        },
    )


@app.post("/search", response_model=SearchResponse, tags=["retrieval"])
async def search(request: SearchRequest) -> SearchResponse:
    if not chunks:
        raise HTTPException(status_code=503, detail="SOP index unavailable")
    results = retriever.search(
        query=request.query,
        equipment=request.equipment,
        alarm_code=request.alarm_code,
        top_k=request.top_k or DEFAULT_TOP_K,
    )
    return SearchResponse(results=results)


@app.post("/reindex", response_model=ReindexResponse, tags=["index"])
async def reindex() -> ReindexResponse:
    global chunks, retriever
    chunks = load_sop_chunks(SOP_FILE_PATH)
    retriever = KeywordRetriever(chunks)
    return ReindexResponse(
        status="ok",
        sop_path=str(SOP_FILE_PATH),
        chunks_indexed=len(chunks),
    )
