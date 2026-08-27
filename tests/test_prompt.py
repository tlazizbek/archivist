from archivist.generation.prompt import build_prompt
from archivist.models import ChunkRecord, ScoredChunk


def make_scored_chunk(chunk_id: int, content: str) -> ScoredChunk:
    return ScoredChunk(
        chunk=ChunkRecord(
            id=chunk_id,
            document_id=1,
            chunk_index=0,
            content=content,
            embedding=None,
        ),
        score=1.0,
        method="keyword",
    )


def test_build_prompt_includes_question_and_context() -> None:
    chunks = [
        make_scored_chunk(1, "Alpha content"),
        make_scored_chunk(2, "Beta content"),
    ]

    prompt = build_prompt("What is alpha?", chunks)

    assert "What is alpha?" in prompt
    assert "Alpha content" in prompt
    assert "Beta content" in prompt


def test_build_prompt_numbers_each_context() -> None:
    chunks = [
        make_scored_chunk(1, "first"),
        make_scored_chunk(2, "second"),
    ]

    prompt = build_prompt("q", chunks)

    assert "--- Context 1 ---" in prompt
    assert "--- Context 2 ---" in prompt


def test_build_prompt_grounds_the_model() -> None:
    prompt = build_prompt("q", [make_scored_chunk(1, "content")])

    assert "using only the provided context" in prompt
    assert "Do not use outside knowledge." in prompt
    assert prompt.rstrip().endswith("Answer:")


def test_build_prompt_handles_no_chunks() -> None:
    prompt = build_prompt("q", [])

    assert "q" in prompt
    assert prompt.rstrip().endswith("Answer:")
