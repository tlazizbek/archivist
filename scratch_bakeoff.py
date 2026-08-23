from archivist.db.database import get_all_chunks
from archivist.generation.llm_client import LLMClient
from archivist.retrieval.keyword import KeywordRetriever
from archivist.retrieval.semantic import SemanticRetriever


chunks = get_all_chunks()

keyword = KeywordRetriever()
keyword.fit(chunks)

client = LLMClient()

semantic = SemanticRetriever(client)
semantic.fit(chunks)


queries = [
    ("Exact term", "organization membership"),
    ("Paraphrase", "How can I become part of an organization?"),
    ("Typo", "organizatoin membership"),
    ("Very short", "username"),
    (
        "Specific/technical",
        "How can I change the email address associated with my GitHub account?",
    ),
]


for category, query in queries:
    keyword_results = keyword.search(query, top_k=3)
    semantic_results = semantic.search(query, top_k=3)

    print("\n" + "=" * 70)
    print(category)
    print(f"Query: {query}")

    print("\nKEYWORD")

    for result in keyword_results:
        print(
            f"{result.score:.3f} | "
            f"chunk {result.chunk.id} | "
            f"{result.chunk.content[:100]}"
        )

    for result in semantic_results:
        print(
            f"{result.score:.3f} | "
            f"chunk {result.chunk.id} | "
            f"{result.chunk.content[:100]}"
        )