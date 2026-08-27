import pytest
from fastapi.testclient import TestClient

from archivist.api import app as app_module
from archivist.models import ChunkRecord, ScoredChunk


class StubRetriever:
    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        chunk = ChunkRecord(
            id=7,
            document_id=3,
            chunk_index=0,
            content="stub chunk",
            embedding=None,
        )
        return [ScoredChunk(chunk=chunk, score=1.0, method="stub")]


class StubRetrieverState:
    def __init__(self) -> None:
        self.requested_methods: list[str] = []
        self.rebuild_count = 0

    def rebuild(self) -> None:
        self.rebuild_count += 1

    def for_method(self, method: str) -> StubRetriever:
        self.requested_methods.append(method)
        return StubRetriever()


class StubLLMClient:
    def complete(self, prompt: str) -> str:
        return "stub answer"


@pytest.fixture
def client(monkeypatch) -> TestClient:
    state = StubRetrieverState()
    monkeypatch.setattr(app_module, "retrievers", state)
    monkeypatch.setattr(app_module, "LLMClient", StubLLMClient)
    monkeypatch.setattr(app_module, "log_query", lambda entry: 1)
    # Bare TestClient (no context manager) skips the DB-touching lifespan.
    return TestClient(app_module.app)


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer_and_sources(client: TestClient) -> None:
    response = client.post(
        "/query",
        json={"question": "how do I change my username?", "method": "keyword"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["answer"] == "stub answer"
    assert body["sources"] == [{"chunk_id": 7, "document_id": 3}]
    assert body["latency_ms"] >= 0


def test_query_defaults_to_hybrid_method(client: TestClient) -> None:
    response = client.post("/query", json={"question": "anything"})

    assert response.status_code == 200
    assert app_module.retrievers.requested_methods == ["hybrid"]


def test_query_rejects_unknown_method(client: TestClient) -> None:
    response = client.post(
        "/query",
        json={"question": "anything", "method": "made-up"},
    )

    assert response.status_code == 422


def test_ingest_rebuilds_retrievers(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(app_module, "ingest", lambda path: (2, 5))

    response = client.post("/ingest", json={"path": "/some/folder"})

    assert response.status_code == 200
    assert response.json() == {"documents_ingested": 2, "chunks_created": 5}
    assert app_module.retrievers.rebuild_count == 1
