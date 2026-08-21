from dataclasses import dataclass


@dataclass
class RawDocument:
    path: str
    title: str
    source_type: str
    raw_text: str


@dataclass
class Chunk:
    document_id: int
    chunk_index: int
    content: str
    token_count: int


@dataclass
class ChunkRecord:
    id: int
    document_id: int
    chunk_index: int
    content: str
    embedding: list[float]


@dataclass
class ScoredChunk:
    chunk: ChunkRecord
    score: float
    method: str


@dataclass
class QueryLogEntry:
    query_text: str
    retrieval_method: str
    retrieved_chunk_ids: list[int]
    answer_text: str
    latency_ms: float
    llm_model: str