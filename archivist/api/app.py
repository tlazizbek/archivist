from fastapi import FastAPI

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
    raise NotImplementedError