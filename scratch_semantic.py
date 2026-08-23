from archivist.db.database import get_all_chunks
from archivist.generation.llm_client import LLMClient
from archivist.retrieval.semantic import SemanticRetriever


chunks = get_all_chunks()

client = LLMClient()
retriever = SemanticRetriever(client)

print(f"Embedding {len(chunks)} chunks...")

retriever.fit(chunks)

queries = [
    "GitHub account management",
    "organization membership",
    "personal profile",
]

for query in queries:
    results = retriever.search(query, top_k=3)

    print(f"\nQuery: {query}")

    for result in results:
        print(
            f"score={result.score:.3f} "
            f"chunk={result.chunk.id} "
            f"content={result.chunk.content[:100]!r}"
        )
