import hashlib
import sqlite3
import json
from pathlib import Path
from sqlite3 import Connection

from archivist.config import DB_PATH
from archivist.models import Chunk, ChunkRecord, RawDocument, QueryLogEntry


from archivist.config import DB_PATH

def get_connection() -> Connection:
    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    return connection

def init_db() -> None:
    connection = get_connection()

    try:
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="utf-8")
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()

def insert_document(doc: RawDocument) -> int | None:
    content_hash = hashlib.sha256(
        doc.raw_text.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    try:
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

        connection.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to insert document")

        return cursor.lastrowid
    finally:
        connection.close()

def insert_chunks(document_id: int, chunks: list[Chunk]) -> None:
    connection = get_connection()

    try:
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

        connection.commit()
    finally:
        connection.close()

def get_all_chunks() -> list[ChunkRecord]:
    connection = get_connection()

    try:
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
    finally:
        connection.close()

def log_query(entry: QueryLogEntry) -> int:
    connection = get_connection()

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
            json.dumps(entry.retrieved_chunk_ids),
            entry.answer_text,
            entry.latency_ms,
            entry.llm_model,
        ),
    )

    connection.commit()
    if cursor.lastrowid is None:
        raise RuntimeError("Failed to get inserted query log ID")

    return cursor.lastrowid