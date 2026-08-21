from dataclasses import dataclass
from pathlib import Path


@dataclass
class RawDocument:
    path: Path
    title: str
    source_type: str
    raw_text: str


@dataclass
class Chunk:
    document_id: int
    chunk_index: int
    content: str
    token_count: int | None


@dataclass
class ChunkRecord:
    id: int
    document_id: int
    chunk_index: int
    content: str
    embedding: bytes | None


@dataclass
class ScoredChunk:
    chunk: ChunkRecord
    score: float
    method: str


@dataclass
class QueryLogEntry:
    query_text: str
    retrieval_method: str
    retrieved_chunk_ids: str | None
    answer_text: str | None
    latency_ms: int | None
    llm_model: str | None