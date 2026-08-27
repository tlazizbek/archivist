import time
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI

from archivist.db.database import get_all_chunks, log_query
from archivist.generation.llm_client import LLMClient
from archivist.generation.prompt import build_prompt
from archivist.models import QueryLogEntry
from archivist.retrieval.hybrid import HybridRetriever
from archivist.retrieval.keyword import KeywordRetriever
from archivist.retrieval.semantic import SemanticRetriever
from archivist.cli import ingest


from archivist.api.schemas import(
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
)


class RetrieverState:
    """Holds retrievers fitted once over all chunks and reused per request."""

    def __init__(self) -> None:
        self.keyword: KeywordRetriever | None = None
        self.semantic: SemanticRetriever | None = None

    def rebuild(self) -> None:
        chunks = get_all_chunks()

        keyword = KeywordRetriever()
        semantic = SemanticRetriever(LLMClient())

        if chunks:
            keyword.fit(chunks)
            semantic.fit(chunks)

        self.keyword = keyword
        self.semantic = semantic

    def for_method(self, method: str):
        if self.keyword is None or self.semantic is None:
            self.rebuild()

        if method == "keyword":
            return self.keyword

        if method == "semantic":
            return self.semantic

        return HybridRetriever(
            keyword=self.keyword,
            semantic=self.semantic,
            weight=0.5,
        )


retrievers = RetrieverState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    retrievers.rebuild()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest_route(body: IngestRequest) -> IngestResponse:
    documents_ingested, chunks_created = ingest(body.path)

    retrievers.rebuild()

    return IngestResponse(
        documents_ingested=documents_ingested,
        chunks_created=chunks_created,
    )

@app.post("/query", response_model=QueryResponse)
def query_route(body: QueryRequest) -> QueryResponse:
    start = time.perf_counter()

    retriever = retrievers.for_method(body.method)
    results = retriever.search(body.question, top_k=5)

    prompt = build_prompt(body.question, results)

    client = LLMClient()
    answer = client.complete(prompt)

    latency_ms = int((time.perf_counter() - start) * 1000)

    retrieved_chunk_ids = json.dumps(
        [result.chunk.id for result in results]
    )

    log_query(
        QueryLogEntry(
            query_text=body.question,
            retrieval_method=body.method,
            retrieved_chunk_ids=retrieved_chunk_ids,
            answer_text=answer,
            latency_ms=latency_ms,
            llm_model="openrouter/free",
        )
    )

    return QueryResponse(
        answer=answer,
        sources=[
            {
                "chunk_id": result.chunk.id,
                "document_id": result.chunk.document_id,
            }
            for result in results
        ],
        latency_ms=latency_ms,
    )
