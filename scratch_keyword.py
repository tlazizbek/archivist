from archivist.db.database import get_all_chunks
from archivist.retrieval.keyword import KeywordRetriever


chunks = get_all_chunks()

retriever = KeywordRetriever()
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
from archivist.db.database import get_connection, get_all_chunks
from archivist.retrieval.keyword import KeywordRetriever


def get_document_title(document_id: int) -> str:
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT title FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()

        if row is None:
            return "Unknown"

        return row["title"]
    finally:
        connection.close()


chunks = get_all_chunks()

retriever = KeywordRetriever()
retriever.fit(chunks)

queries = [
    "GitHub account management",
    "organization membership",
    "personal profile",
]

for query in queries:
    results = retriever.search(query, top_k=1)

    result = results[0]

    title = get_document_title(
        result.chunk.document_id
    )

    print(
        f"Query: {query}\n"
        f"Top result: {title}\n"
        f"Score: {result.score:.3f}\n"
    )
