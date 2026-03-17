from typing import Any, Optional

class KnowledgeBase:
    def __init__(self):
        self._facts: dict[str, dict] = {}
        self._documents: dict[str, dict] = {}

    def add_fact(self, key: str, value: Any, tags: list[str] = None) -> None:
        self._facts[key] = {"value": value, "tags": tags or []}

    def get_fact(self, key: str) -> Optional[Any]:
        entry = self._facts.get(key)
        return entry["value"] if entry else None

    def search_facts(self, query: str) -> list[dict]:
        q = query.lower()
        return [
            {"key": k, "value": v["value"], "tags": v["tags"]}
            for k, v in self._facts.items()
            if q in k.lower()
        ]

    def add_document(self, doc_id: str, content: str, metadata: dict = None) -> None:
        self._documents[doc_id] = {"doc_id": doc_id, "content": content, "metadata": metadata or {}}

    def get_document(self, doc_id: str) -> Optional[dict]:
        return self._documents.get(doc_id)

    def list_documents(self) -> list[dict]:
        return list(self._documents.values())
