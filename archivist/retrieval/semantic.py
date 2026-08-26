import pickle

import numpy as np

from typing import Protocol
from sklearn.metrics.pairwise import cosine_similarity

from archivist.models import ChunkRecord, ScoredChunk


class EmbeddingClient(Protocol):
    def embed(self, text: str) -> list[float]:
        ...


class SemanticRetriever:
    def __init__(self, client: EmbeddingClient) -> None:
        self.client = client
        self.chunks: list[ChunkRecord] = []
        self.vectors: np.ndarray | None = None

    def fit(self, chunks: list[ChunkRecord]) -> None:
        self.chunks = chunks

        vectors = []

        for chunk in chunks:
            if chunk.embedding is not None:
                vectors.append(pickle.loads(chunk.embedding))
            else:
                vectors.append(self.client.embed(chunk.content))

        self.vectors = np.array(vectors, dtype=float)

    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        if self.vectors is None:
            raise RuntimeError("Retriever has not been fitted")

        if not self.chunks:
            return []

        query_vector = np.array(
            self.client.embed(query),
            dtype=float,
        ).reshape(1, -1)

        scores = cosine_similarity(
            query_vector,
            self.vectors,
        ).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            ScoredChunk(
                chunk=self.chunks[index],
                score=float(scores[index]),
                method="semantic",
            )
            for index in top_indices
        ]