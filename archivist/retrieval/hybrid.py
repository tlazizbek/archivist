import numpy as np

from archivist.models import ScoredChunk

class HybridRetriever:
    def __init__(self, keyword, semantic, weight: float) -> float:
        self.keyword = keyword
        self.semantic = semantic
        self.weight = weight

    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        keyword_results = self.keyword.search(query, top_k)
        semantic_results = self.semantic.search(query, top_k)

        keyword_scores = {
            result.chunk.id: result.score
            for result in keyword_results
        }

        semantic_scores = {
            result.chunk.id: result.score
            for result in semantic_results
        }

        all_chunk_ids = set(keyword_scores) | set(semantic_scores)

        if not all_chunk_ids:
            return []

        keyword_values = list(keyword_scores.values())
        semantic_values = list(semantic_scores.values())

        keyword_min = min(keyword_values) if keyword_values else 0.0
        keyword_max = max(keyword_values) if keyword_values else 0.0

        semantic_min = min(semantic_values) if semantic_values else 0.0
        semantic_max = max(semantic_values) if semantic_values else 0.0

        def normalize(
            score: float,
            minimum: float,
            maximum: float,
        ) -> float:
            if maximum == minimum:
                return 1.0

            normalized = (score - minimum) / (maximum - minimum)
            return float(np.clip(normalized, 0.0, 1.0))

        chunks = {}

        for result in keyword_results:
            chunks[result.chunk.id] = result.chunk

        for result in semantic_results:
            chunks[result.chunk.id] = result.chunk

        combined_results = []

        for chunk_id in all_chunk_ids:
            keyword_score = normalize(
                keyword_scores.get(chunk_id, 0.0),
                keyword_min,
                keyword_max
            )

            semantic_score = normalize(
                semantic_scores.get(chunk_id, 0.0),
                semantic_min,
                semantic_max,
            )

            combined_score = (
                self.weight * semantic_score
                + (1 - self.weight) * keyword_score
            )

            combined_results.append(
                ScoredChunk(
                    chunk=chunks[chunk_id],
                    score=combined_score,
                    method="hybrid"
                )
            )

        combined_results.sort(
            key=lambda result: result.score,
            reverse=True
        )

        return combined_results[:top_k]