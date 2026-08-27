import hashlib
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path
from sqlite3 import Connection

from archivist import config
from archivist.models import Chunk, ChunkRecord, RawDocument, QueryLogEntry


def get_connection() -> Connection:
    connection = sqlite3.connect(
        config.DB_PATH,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connect() -> Iterator[Connection]:
    """Yield a connection that is committed on success and always closed."""
    connection = get_connection()

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with connect() as connection:
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="utf-8")
        connection.executescript(schema)

def insert_document(doc: RawDocument) -> int | None:
    content_hash = hashlib.sha256(
        doc.raw_text.encode("utf-8")
    ).hexdigest()

    with connect() as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM documents
            WHERE content_hash = ?
            """,
            (content_hash,),
        ).fetchone()

        if existing is not None:
            return None

        cursor = connection.execute(
            """
            INSERT INTO documents (
                title,
                source_path,
                source_type,
                content_hash
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                doc.title,
                str(doc.path),
                doc.source_type,
                content_hash,
            ),
        )

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to insert document")

        return cursor.lastrowid

def insert_chunks(document_id: int, chunks: list[Chunk]) -> None:
    with connect() as connection:
        connection.executemany(
            """
            INSERT INTO chunks (
                document_id,
                chunk_index,
                content,
                token_count
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    document_id,
                    chunk.chunk_index,
                    chunk.content,
                    chunk.token_count,
                )
                for chunk in chunks
            ],
        )

def get_all_chunks() -> list[ChunkRecord]:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                document_id,
                chunk_index,
                content,
                embedding
            FROM chunks
            ORDER BY id
            """
        ).fetchall()

        return [
            ChunkRecord(
                id=row["id"],
                document_id=row["document_id"],
                chunk_index=row["chunk_index"],
                content=row["content"],
                embedding=row["embedding"],
            )
            for row in rows
        ]

def update_chunk_embeddings(
    embeddings: list[tuple[int, bytes]]
) -> None:
    with connect() as connection:
        connection.executemany(
            """
            UPDATE chunks
            SET embedding = ?
            WHERE id = ?
            """,
            [
                (embedding, chunk_id)
                for chunk_id, embedding in embeddings
            ]
        )

def log_query(entry: QueryLogEntry) -> int:
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO query_logs (
                query_text,
                retrieval_method,
                retrieved_chunk_ids,
                answer_text,
                latency_ms,
                llm_model
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry.query_text,
                entry.retrieval_method,
                entry.retrieved_chunk_ids,
                entry.answer_text,
                entry.latency_ms,
                entry.llm_model,
            ),
        )

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to get inserted query log ID")

        return cursor.lastrowid
