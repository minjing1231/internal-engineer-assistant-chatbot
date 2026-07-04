from pathlib import Path

from services.rag_retrieval.app.ingestion.markdown_loader import load_sop_chunks
from services.rag_retrieval.app.retrieval.keyword_search import KeywordRetriever


SOP_PATH = Path(__file__).resolve().parents[3] / "document" / "SOP.md"


def test_load_sop_chunks_extracts_metadata():
    chunks = load_sop_chunks(SOP_PATH)

    rf101_chunks = [chunk for chunk in chunks if chunk.source_id == "SOP-ETCH-001"]

    assert len(chunks) >= 30
    assert rf101_chunks
    assert rf101_chunks[0].alarm_code == "RF101"
    assert rf101_chunks[0].severity == "High"
    assert "Etcher-03" in rf101_chunks[0].equipment


def test_exact_alarm_match_ranks_correct_sop_first():
    chunks = load_sop_chunks(SOP_PATH)
    retriever = KeywordRetriever(chunks)

    results = retriever.search(
        query="Etcher-03 triggered RF101 during plasma ignition",
        equipment="Etcher-03",
        alarm_code="RF101",
        top_k=3,
    )

    assert results
    assert results[0].source_id == "SOP-ETCH-001"
    assert all(result.score > 0 for result in results)
