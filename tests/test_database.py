from pathlib import Path

import pytest

from archivist import config
from archivist.db import database
from archivist.models import Chunk, QueryLogEntry, RawDocument


@pytest.fixture
def temp_db(tmp_path: Path, monkeypatch) -> Path:
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(config, "DB_PATH", db_path)
    database.init_db()
    return db_path


def make_document() -> RawDocument:
    return RawDocument(
        path=Path("doc.txt"),
        title="Doc",
        source_type="text",
        raw_text="hello world",
    )


def test_insert_document_returns_id(temp_db: Path) -> None:
    document_id = database.insert_document(make_document())

    assert document_id == 1


def test_insert_document_deduplicates_by_content(temp_db: Path) -> None:
    first = database.insert_document(make_document())
    second = database.insert_document(make_document())

    assert first == 1
    assert second is None


def test_insert_and_read_chunks_preserves_order(temp_db: Path) -> None:
    document_id = database.insert_document(make_document())

    database.insert_chunks(
        document_id,
        [
            Chunk(document_id, 0, "first", 1),
            Chunk(document_id, 1, "second", 1),
        ],
    )

    chunks = database.get_all_chunks()

    assert [chunk.content for chunk in chunks] == ["first", "second"]
    assert all(chunk.embedding is None for chunk in chunks)


def test_update_chunk_embeddings_persists_bytes(temp_db: Path) -> None:
    document_id = database.insert_document(make_document())
    database.insert_chunks(document_id, [Chunk(document_id, 0, "first", 1)])

    chunk_id = database.get_all_chunks()[0].id
    database.update_chunk_embeddings([(chunk_id, b"vector-bytes")])

    stored = database.get_all_chunks()[0]
    assert stored.embedding == b"vector-bytes"


def test_log_query_returns_id_and_persists(temp_db: Path) -> None:
    entry = QueryLogEntry(
        query_text="q",
        retrieval_method="keyword",
        retrieved_chunk_ids="[1]",
        answer_text="a",
        latency_ms=5,
        llm_model="test",
    )

    log_id = database.log_query(entry)

    assert log_id == 1

    with database.connect() as connection:
        row = connection.execute(
            "SELECT query_text FROM query_logs WHERE id = ?",
            (log_id,),
        ).fetchone()

    assert row["query_text"] == "q"
