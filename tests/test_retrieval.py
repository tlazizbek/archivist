from archivist.models import ChunkRecord
from archivist.retrieval.keyword import KeywordRetriever
from archivist.retrieval.semantic import SemanticRetriever


class FakeEmbeddingClient:
    def embed(self, text: str) -> list[float]:
        if "username" in text.lower():
            return [1.0, 0.0, 0.0]

        if "email" in text.lower():
            return [0.0, 1.0, 0.0]

        return [0.0, 0.0, 1.0]


def make_chunks() -> list[ChunkRecord]:
    return [
        ChunkRecord(
            id=1,
            document_id=1,
            chunk_index=0,
            content="You can change your GitHub username from your account settings.",
            embedding=None,
        ),
        ChunkRecord(
            id=2,
            document_id=1,
            chunk_index=1,
            content="You can add or remove email addresses from your GitHub account.",
            embedding=None,
        ),
        ChunkRecord(
            id=3,
            document_id=1,
            chunk_index=2,
            content="Organizations allow multiple people to collaborate on repositories.",
            embedding=None,
        ),
    ]


def test_keyword_retriever_returns_correct_chunk() -> None:
    chunks = make_chunks()

    retriever = KeywordRetriever()
    retriever.fit(chunks)

    results = retriever.search("change GitHub username", top_k=1)

    assert results[0].chunk.id == 1


def test_semantic_retriever_returns_correct_chunk() -> None:
    chunks = make_chunks()

    retriever = SemanticRetriever(FakeEmbeddingClient())
    retriever.fit(chunks)

    results = retriever.search("change GitHub username", top_k=1)

    assert results[0].chunk.id == 1