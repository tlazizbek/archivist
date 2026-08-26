from archivist.models import ScoredChunk


def build_prompt(query: str, chunks: list[ScoredChunk]) -> str:
    context_parts = []

    for index, scored_chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"--- Context {index} ---\n"
            f"{scored_chunk.chunk.content}"
        )

    context = "\n\n".join(context_parts)

    return (
        "Answer the user's question using only the provided context.\n"
        "If the answer cannot be found in the provided context, say that "
        "you do not have enough information.\n"
        "Do not use outside knowledge.\n\n"
        f"Context:\n\n{context}\n\n"
        f"User question:\n{query}\n\n"
        "Answer:"
    )