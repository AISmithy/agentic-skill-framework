"""In-process vector store using cosine similarity (no external deps)."""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass, field
from typing import Any


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class VectorDocument:
    doc_id: str
    text: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    doc_id: str
    text: str
    score: float
    metadata: dict[str, Any]


class VectorStore:
    """
    Minimal in-process vector similarity search.

    For production, swap with pgvector, Pinecone, or Weaviate.
    Embeddings are provided externally (e.g., from an LLM API).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._documents: dict[str, VectorDocument] = {}

    def upsert(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        doc = VectorDocument(
            doc_id=doc_id,
            text=text,
            embedding=embedding,
            metadata=metadata or {},
        )
        with self._lock:
            self._documents[doc_id] = doc

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        with self._lock:
            docs = list(self._documents.values())

        scored = [
            (doc, _cosine_similarity(query_embedding, doc.embedding))
            for doc in docs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            SearchResult(
                doc_id=doc.doc_id,
                text=doc.text,
                score=round(score, 4),
                metadata=doc.metadata,
            )
            for doc, score in scored[:top_k]
            if score >= min_score
        ]

    def delete(self, doc_id: str) -> None:
        with self._lock:
            self._documents.pop(doc_id, None)

    def count(self) -> int:
        with self._lock:
            return len(self._documents)
