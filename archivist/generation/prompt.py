from archivist.models import ScoredChunk


def build_prompt(query: str, chunks: list[ScoredChunk]) -> str:
    context_parts = []

    for index, scored_chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"--- Context {index} ---\n"
            f"{scored_chunk.chunk.content}"
        )

    context = "\n\n".join(context_parts)

    return f"""Answer the user's question using only the provided context.

               If the answer cannot be found in the provided context, say that you do not have enough information.

               Do not use outside knowledge.

               Context:

               {context}

               User question:
               {query}

               Answer:"""