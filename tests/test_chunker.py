from pathlib import Path

from archivist.ingestion.chunker import chunk_document, chunk_text
from archivist.models import RawDocument


def test_short_text_produces_one_chunk():
    text = "This is a short document."

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=10,
    )

    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_produces_overlapping_chunks():
    text = " ".join(f"word{i}" for i in range(10))

    chunks = chunk_text(
        text,
        chunk_size=5,
        overlap=2,
    )

    assert len(chunks) == 3
    assert chunks[0] == "word0 word1 word2 word3 word4"
    assert chunks[1] == "word3 word4 word5 word6 word7"
    assert chunks[2] == "word6 word7 word8 word9"


def test_chunk_document_assigns_indexes():
    document = RawDocument(
        path=Path("test.txt"),
        title="Test",
        source_type="txt",
        raw_text=" ".join(f"word{i}" for i in range(10)),
    )

    chunks = chunk_document(
        document,
        chunk_size=5,
        overlap=2,
    )

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert all(chunk.document_id == 0 for chunk in chunks)