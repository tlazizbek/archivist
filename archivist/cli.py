import argparse

from archivist import config
from archivist.db.database import get_all_chunks, init_db, insert_chunks, insert_document
from archivist.embedding import embed_missing_chunks
from archivist.ingestion.chunker import chunk_document
from archivist.ingestion.cleaner import clean
from archivist.ingestion.loaders import load_folder

PLACEHOLDER_VALUES = {
    "",
    "your-api-key",
    "your-llm-base-url",
    "https://your-provider/api/v1",
}


def ingest(path: str) -> tuple[int, int]:
    init_db()

    documents_ingested = 0
    chunks_created = 0

    documents = load_folder(path)

    for document in documents:
        document.raw_text = clean(document.raw_text)

        chunks = chunk_document(
            document,
            chunk_size=500,
            overlap=50,
        )

        document_id = insert_document(document)

        if document_id is None:
            print(f"Skipped: {document.title}")
            continue

        insert_chunks(document_id, chunks)

        documents_ingested += 1
        chunks_created += len(chunks)

        print(f"Ingested: {document.title} ({len(chunks)} chunks)")

    return documents_ingested, chunks_created


def _missing_config() -> list[str]:
    return [
        name
        for name, value in (
            ("LLM_API_KEY", config.LLM_API_KEY),
            ("LLM_BASE_URL", config.LLM_BASE_URL),
        )
        if value in PLACEHOLDER_VALUES
    ]


def start(docs: str | None, port: int) -> None:
    """Set up everything and launch the server in one step."""
    missing = _missing_config()

    if missing:
        print("Archivist is not configured yet.")
        print(
            f"Please open the .env file and fill in: {', '.join(missing)}."
        )
        print("See .env.example for the format, then run this again.")
        return

    init_db()

    if docs:
        print(f"Reading documents from {docs}...")
        ingest(docs)

    if not get_all_chunks():
        print("There are no documents to search yet.")
        print("Add some by running again with a folder, for example:")
        print("    archivist start --docs data/raw")
        return

    print("Preparing the search index (this can take a moment)...")
    embedded = embed_missing_chunks(on_progress=print)
    print(
        f"Added {embedded} new pieces to the index."
        if embedded
        else "Search index is ready."
    )

    url = f"http://127.0.0.1:{port}"
    print()
    print("Archivist is starting up.")
    print(f"Open {url}/docs in your browser to ask questions.")
    print("Press Ctrl+C here to stop it.")
    print()

    import uvicorn

    uvicorn.run("archivist.api.app:app", host="127.0.0.1", port=port)


def main() -> None:
    parser = argparse.ArgumentParser(description="Archivist")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest a folder of documents",
    )
    ingest_parser.add_argument(
        "path",
        type=str,
        help="Folder to ingest",
    )

    start_parser = subparsers.add_parser(
        "start",
        help="Set up and launch Archivist in one step",
    )
    start_parser.add_argument(
        "--docs",
        type=str,
        default=None,
        help="Folder of documents to add before starting",
    )
    start_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
    )

    args = parser.parse_args()

    match args.command:
        case "ingest":
            ingest(args.path)
        case "start":
            start(args.docs, args.port)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
