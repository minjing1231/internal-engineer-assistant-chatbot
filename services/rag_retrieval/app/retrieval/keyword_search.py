import math
import re

from ..schemas import SopContextChunk


TOKEN_RE = re.compile(r"[A-Za-z0-9-]+")


def tokenize(text: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(text)]


class KeywordRetriever:
    def __init__(self, chunks: list[SopContextChunk]):
        self.chunks = chunks

    def search(
        self,
        query: str,
        equipment: str | None = None,
        alarm_code: str | None = None,
        top_k: int = 4,
    ) -> list[SopContextChunk]:
        query_tokens = tokenize(" ".join([query, equipment or "", alarm_code or ""]))
        scored = [
            chunk.model_copy(update={"score": self._score(chunk, query_tokens, equipment, alarm_code)})
            for chunk in self.chunks
        ]
        ranked = sorted(scored, key=lambda item: item.score, reverse=True)
        return [item for item in ranked if item.score > 0][:top_k]

    def _score(
        self,
        chunk: SopContextChunk,
        query_tokens: list[str],
        equipment: str | None,
        alarm_code: str | None,
    ) -> float:
        searchable = " ".join(
            [
                chunk.source_id,
                chunk.title,
                chunk.section,
                " ".join(chunk.equipment),
                chunk.alarm_code or "",
                chunk.severity or "",
                chunk.content,
            ]
        )
        doc_tokens = tokenize(searchable)
        if not doc_tokens:
            return 0.0

        doc_token_set = set(doc_tokens)
        overlap = sum(1 for token in query_tokens if token in doc_token_set)
        score = overlap / math.sqrt(len(doc_tokens))

        if alarm_code and chunk.alarm_code and alarm_code.casefold() == chunk.alarm_code.casefold():
            score += 8.0
        if equipment:
            wanted = equipment.casefold()
            if any(wanted == item.casefold() for item in chunk.equipment):
                score += 4.0
        if chunk.section in {"Safety Precautions", "Troubleshooting Steps", "Escalation Criteria"}:
            score += 0.25
        return round(score, 4)
