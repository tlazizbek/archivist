from pydantic import BaseModel
from typing import Literal


class IngestRequest(BaseModel):
    path: str

class IngestResponse(BaseModel):
    documents_ingested: int
    chunks_created: int

class QueryRequest(BaseModel):
    question: str
    method: Literal["keyword", "semantic", "hybrid"] = "hybrid"


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict[str, int]]
    latency_ms: int