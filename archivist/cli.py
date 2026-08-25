import argparse

from archivist.db.database import init_db, insert_chunks, insert_document
from archivist.ingestion.chunker import chunk_document
from archivist.ingestion.cleaner import clean
from archivist.ingestion.loaders import load_folder


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Archivist CLI")
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

    args = parser.parse_args()

    match args.command:
        case "ingest":
            ingest(args.path)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()