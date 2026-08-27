import pickle
from pathlib import Path

import pytest

from archivist import config
from archivist.db import database
from archivist.embedding import embed_missing_chunks
from archivist.models import Chunk, RawDocument


class FakeClient:
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text))] for text in texts]


@pytest.fixture
def temp_db(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    database.init_db()

    document_id = database.insert_document(
        RawDocument(Path("d.txt"), "Doc", "text", "body")
    )
    database.insert_chunks(
        document_id,
        [Chunk(document_id, 0, "alpha", 1), Chunk(document_id, 1, "beta", 1)],
    )


def test_embed_missing_chunks_embeds_and_returns_count(temp_db) -> None:
    embedded = embed_missing_chunks(client=FakeClient())

    assert embedded == 2

    stored = database.get_all_chunks()
    assert all(chunk.embedding is not None for chunk in stored)
    assert pickle.loads(stored[0].embedding) == [5.0]  # len("alpha")


def test_embed_missing_chunks_is_idempotent(temp_db) -> None:
    embed_missing_chunks(client=FakeClient())

    assert embed_missing_chunks(client=FakeClient()) == 0
