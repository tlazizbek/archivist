import re

from archivist.db.database import get_all_chunks
from archivist.generation.llm_client import LLMClient
from archivist.retrieval.keyword import KeywordRetriever
from archivist.retrieval.semantic import SemanticRetriever


chunks = get_all_chunks()

# Build a readable book title per document_id from the header of its first chunk,
# so bake-off output shows "Moby Dick" instead of "pg2701".
titles: dict[int, str] = {}
for chunk in chunks:
    if chunk.document_id in titles:
        continue
    match = re.search(r"eBook of (.+?) This eBook", chunk.content)
    if match:
        titles[chunk.document_id] = match.group(1).strip()

keyword = KeywordRetriever()
keyword.fit(chunks)

client = LLMClient()

semantic = SemanticRetriever(client)
semantic.fit(chunks)


queries = [
    ("Exact term", "whale hunting harpoon"),
    ("Paraphrase", "a young orphan girl adopted by a family living on a farm"),
    ("Typo", "Sherlok Holmes detective"),
    ("Very short", "vampire"),
    (
        "Specific/technical",
        "What creature does the scientist assemble from dead body parts?",
    ),
]


def show(result):
    book = titles.get(result.chunk.document_id, "unknown")
    snippet = " ".join(result.chunk.content.split())[:90]
    print(f"  {result.score:.3f} | chunk {result.chunk.id} | {book} | {snippet}")


for category, query in queries:
    keyword_results = keyword.search(query, top_k=3)
    semantic_results = semantic.search(query, top_k=3)

    print("\n" + "=" * 70)
    print(f"{category}")
    print(f"Query: {query}")

    print("\nKEYWORD")
    for result in keyword_results:
        show(result)

    print("\nSEMANTIC")
    for result in semantic_results:
        show(result)
