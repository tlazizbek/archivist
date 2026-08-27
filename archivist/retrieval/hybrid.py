import numpy as np

from archivist.models import ChunkRecord, ScoredChunk


class ScoreIndex:
    def __init__(self, results: list[ScoredChunk]) -> None:
        self.scores = {result.chunk.id: result.score for result in results}
        self.chunks = {result.chunk.id: result.chunk for result in results}

        values = list(self.scores.values())
        self.minimum = min(values) if values else 0.0
        self.maximum = max(values) if values else 0.0

    def normalized(self, chunk_id: int) -> float:
        if self.maximum == self.minimum:
            return 1.0

        score = self.scores.get(chunk_id, 0.0)
        normalized = (score - self.minimum) / (self.maximum - self.minimum)
        return float(np.clip(normalized, 0.0, 1.0))


class HybridRetriever:
    def __init__(self, keyword, semantic, weight: float) -> None:
        self.keyword = keyword
        self.semantic = semantic
        self.weight = weight

    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        keyword = ScoreIndex(self.keyword.search(query, top_k))
        semantic = ScoreIndex(self.semantic.search(query, top_k))

        chunk_ids = set(keyword.scores) | set(semantic.scores)

        if not chunk_ids:
            return []

        chunks: dict[int, ChunkRecord] = {**keyword.chunks, **semantic.chunks}

        combined_results = [
            ScoredChunk(
                chunk=chunks[chunk_id],
                score=(
                    self.weight * semantic.normalized(chunk_id)
                    + (1 - self.weight) * keyword.normalized(chunk_id)
                ),
                method="hybrid",
            )
            for chunk_id in chunk_ids
        ]

        combined_results.sort(key=lambda result: result.score, reverse=True)

        return combined_results[:top_k]
