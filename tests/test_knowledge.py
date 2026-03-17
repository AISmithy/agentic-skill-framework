import pytest
from agentic_skill_framework import SessionMemory, VectorStore, KnowledgeBase, ArtifactStore

class TestSessionMemory:
    def test_store_retrieve(self):
        mem = SessionMemory()
        mem.store("sess1", "key1", "value1")
        assert mem.retrieve("sess1", "key1") == "value1"
        assert mem.retrieve("sess1", "missing") is None
        assert mem.retrieve("no_session", "key1") is None

    def test_history(self):
        mem = SessionMemory()
        mem.append_history("sess1", {"msg": "hello"})
        mem.append_history("sess1", {"msg": "world"})
        history = mem.get_history("sess1")
        assert len(history) == 2
        assert mem.get_history("no_session") == []

    def test_clear(self):
        mem = SessionMemory()
        mem.store("sess1", "k", "v")
        mem.append_history("sess1", {"x": 1})
        mem.clear("sess1")
        assert mem.retrieve("sess1", "k") is None
        assert mem.get_history("sess1") == []


class TestVectorStore:
    def test_add_and_count(self):
        vs = VectorStore()
        vs.add("doc1", "hello world")
        vs.add("doc2", "goodbye world")
        assert vs.count() == 2

    def test_search(self):
        vs = VectorStore()
        vs.add("doc1", "machine learning algorithms", {"topic": "ml"})
        vs.add("doc2", "cooking recipes and food", {"topic": "cooking"})
        results = vs.search("machine learning", top_k=2)
        assert results[0]["doc_id"] == "doc1"
        assert results[0]["score"] > 0

    def test_delete(self):
        vs = VectorStore()
        vs.add("doc1", "test")
        assert vs.delete("doc1") is True
        assert vs.count() == 0
        assert vs.delete("nonexistent") is False


class TestKnowledgeBase:
    def test_facts(self):
        kb = KnowledgeBase()
        kb.add_fact("capital_france", "Paris", tags=["geography"])
        assert kb.get_fact("capital_france") == "Paris"
        assert kb.get_fact("missing") is None

    def test_search_facts(self):
        kb = KnowledgeBase()
        kb.add_fact("capital_france", "Paris")
        kb.add_fact("capital_germany", "Berlin")
        kb.add_fact("population_france", 67e6)
        results = kb.search_facts("capital")
        names = [r["key"] for r in results]
        assert "capital_france" in names
        assert "capital_germany" in names
        assert "population_france" not in names

    def test_documents(self):
        kb = KnowledgeBase()
        kb.add_document("doc1", "some content", {"author": "alice"})
        doc = kb.get_document("doc1")
        assert doc["content"] == "some content"
        assert len(kb.list_documents()) == 1


class TestArtifactStore:
    def test_save_and_load(self):
        store = ArtifactStore()
        store.save("art1", {"data": [1, 2, 3]}, "json_data", {"version": "1"})
        loaded = store.load("art1")
        assert loaded["data"] == {"data": [1, 2, 3]}
        assert loaded["artifact_type"] == "json_data"

    def test_list_artifacts(self):
        store = ArtifactStore()
        store.save("a1", "x", "text")
        store.save("a2", "y", "text")
        store.save("a3", 123, "number")
        assert len(store.list_artifacts()) == 3
        assert len(store.list_artifacts("text")) == 2
        assert len(store.list_artifacts("number")) == 1

    def test_delete(self):
        store = ArtifactStore()
        store.save("art1", "data", "type1")
        assert store.delete("art1") is True
        assert store.load("art1") is None
        assert store.delete("nonexistent") is False
