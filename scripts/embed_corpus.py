from archivist.embedding import embed_missing_chunks


def main() -> None:
    embedded = embed_missing_chunks(on_progress=print)

    if embedded:
        print(f"Embedding generation complete. Embedded {embedded} chunks.")
    else:
        print("All chunks already have embeddings.")


if __name__ == "__main__":
    main()
