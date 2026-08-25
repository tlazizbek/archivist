import time
import json
from fastapi import FastAPI

from archivist.db.database import get_all_chunks, log_query
from archivist.generation.llm_client import LLMClient
from archivist.generation.prompt import build_prompt
from archivist.models import QueryLogEntry
from archivist.retrieval.hybrid import HybridRetriever
from archivist.retrieval.keyword import KeywordRetriever
from archivist.retrieval.semantic import SemanticRetriever


from archivist.api.schemas import(
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
)


app = FastAPI()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest_route(body: IngestRequest) -> IngestResponse:
    raise NotImplementedError

@app.post("/query", response_model=QueryResponse)
def query_route(body: QueryRequest) -> QueryResponse:
    start = time.perf_counter()

    chunks = get_all_chunks()

    keyword = KeywordRetriever()
    keyword.fit(chunks)

    semantic = SemanticRetriever(LLMClient())
    semantic.fit(chunks)

    hybrid =HybridRetriever(
        keyword=keyword,
        semantic=semantic,
        weight=0.5,
    )

    results = hybrid.search(body.question, top_k=5)

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
