from archivist.models import Chunk, RawDocument


def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start = end - overlap

    return chunks


def chunk_document(
    doc: RawDocument,
    chunk_size: int,
    overlap: int,
) -> list[Chunk]:
    text_chunks = chunk_text(doc.raw_text, chunk_size, overlap)

    return  [
        Chunk(
            document_id=0,
            chunk_index=index,
            content=content,
            token_count=len(content.split()),
        )
        for index, content in enumerate(text_chunks)
    ]