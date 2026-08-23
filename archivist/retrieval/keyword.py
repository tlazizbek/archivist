import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from archivist.models import ChunkRecord, ScoredChunk


class KeywordRetriever:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer()
        self.chunks: list[ChunkRecord] = []
        self.matrix = None

    def fit(self, chunks: list[ChunkRecord]) -> None:
        self.chunks = chunks

        texts = [chunk.content for chunk in chunks]

        self.matrix = self.vectorizer.fit_transform(texts)

    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        if self.matrix is None:
            raise RuntimeError("Retriever has not been fitted")

        if not self.chunks:
            return []

        query_vector = self.vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            self.matrix,
        ).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            ScoredChunk(
                chunk=self.chunks[index],
                score=float(scores[index]),
                method="keyword",
            )
            for index in top_indices
        ]