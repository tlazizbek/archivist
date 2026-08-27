import pickle
from collections.abc import Callable

from archivist.db.database import get_all_chunks, update_chunk_embeddings
from archivist.generation.llm_client import LLMClient

BATCH_SIZE = 50


def embed_missing_chunks(
    client: LLMClient | None = None,
    on_progress: Callable[[str], None] = lambda message: None,
) -> int:
    """Embed every chunk that has no embedding yet.

    Returns the number of chunks embedded. Already-embedded chunks are
    skipped, so this is cheap to re-run.
    """
    client = client or LLMClient()

    missing = [
        chunk
        for chunk in get_all_chunks()
        if chunk.embedding is None
    ]

    if not missing:
        return 0

    total = len(missing)

    for start in range(0, total, BATCH_SIZE):
        batch = missing[start:start + BATCH_SIZE]

        on_progress(
            f"Embedding pieces {start + 1}-{start + len(batch)} of {total}..."
        )

        vectors = client.embed_batch([chunk.content for chunk in batch])

        update_chunk_embeddings(
            [
                (chunk.id, pickle.dumps(vector))
                for chunk, vector in zip(batch, vectors)
            ]
        )

    return total
