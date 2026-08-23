import argparse

from archivist.db.database import init_db, insert_chunks, insert_document
from archivist.ingestion.chunker import chunk_document
from archivist.ingestion.cleaner import clean
from archivist.ingestion.loaders import load_folder


def ingest(path: str) -> None:
    init_db()

    documents = load_folder(path)

    for document in documents:
        document.raw_text = clean(document.raw_text)

        chunks = chunk_document(
            document,
            chunk_size=500,
            overlap=50,
        )

        document_id = insert_document(document)

        insert_chunks(document_id, chunks)


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