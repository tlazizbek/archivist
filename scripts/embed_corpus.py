import pickle

from archivist.db.database import get_all_chunks, update_chunk_embeddings
from archivist.generation.llm_client import LLMClient


BATCH_SIZE = 50


def main() -> None:
    chunks = get_all_chunks()

    missing = [
        chunk
        for chunk in chunks
        if chunk.embedding is None
    ]

    print(f"Total chunks: {len(chunks)}")
    print(f"Missing embeddings: {len(missing)}")

    if not missing:
        print("All chunks already have embeddings.")
        return

    client = LLMClient()

    total = len(missing)

    for start in range(0, total, BATCH_SIZE):
        batch = missing[start:start + BATCH_SIZE]

        texts = [
            chunk.content
            for chunk in batch
        ]

        print(
            f"Embedding chunks "
            f"{start + 1}-{start + len(batch)} "
            f"of {total}..."
        )

        vectors = client.embed_batch(texts)

        rows = [
            (
                chunk.id,
                pickle.dumps(vector),
            )
            for chunk, vector in zip(batch, vectors)
        ]

        update_chunk_embeddings(rows)

    print("Embedding generation complete.")


if __name__ == "__main__":
    main()