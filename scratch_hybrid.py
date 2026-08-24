from archivist.db.database import get_all_chunks
from archivist.generation.llm_client import LLMClient
from archivist.retrieval.keyword import KeywordRetriever
from archivist.retrieval.semantic import SemanticRetriever
from archivist.retrieval.hybrid import HybridRetriever


chunks = get_all_chunks()

keyword = KeywordRetriever()
keyword.fit(chunks)

semantic = SemanticRetriever(LLMClient())
semantic.fit(chunks)

hybrid = HybridRetriever(
    keyword=keyword,
    semantic=semantic,
    weight=0.5,
)

queries = [
    "organization membership",
    "How can I become part of an organization?",
    "organizatoin membership",
    "username",
    "How can I change the email address associated with my GitHub account?",
]

for query in queries:
    results = hybrid.search(query, top_k=3)

    print(f"\nQuery: {query}")

    for result in results:
        print(
            f"{result.score:.3f} | "
            f"chunk {result.chunk.id} | "
            f"{result.chunk.content[:100]}"
        )
