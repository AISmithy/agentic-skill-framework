import re
import math
from typing import Optional

class VectorStore:
    def __init__(self):
        self._docs: dict[str, dict] = {}

    def _vectorize(self, text: str) -> dict[str, float]:
        words = re.split(r'[\s\W]+', text.lower())
        words = [w for w in words if w]
        if not words:
            return {}
        total = len(words)
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return {w: c / total for w, c in freq.items()}

    def _cosine_similarity(self, v1: dict, v2: dict) -> float:
        dot = sum(v1.get(k, 0) * v2.get(k, 0) for k in v2)
        mag1 = math.sqrt(sum(x * x for x in v1.values()))
        mag2 = math.sqrt(sum(x * x for x in v2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    def add(self, doc_id: str, text: str, metadata: dict = None) -> None:
        self._docs[doc_id] = {
            "text": text,
            "metadata": metadata or {},
            "vector": self._vectorize(text)
        }

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        qvec = self._vectorize(query)
        results = []
        for doc_id, doc in self._docs.items():
            score = self._cosine_similarity(qvec, doc["vector"])
            results.append({"doc_id": doc_id, "text": doc["text"], "score": score, "metadata": doc["metadata"]})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete(self, doc_id: str) -> bool:
        if doc_id in self._docs:
            del self._docs[doc_id]
            return True
        return False

    def count(self) -> int:
        return len(self._docs)
