import pandas as pd

from archivist.db.database import get_connection


def export_query_logs() -> pd.DataFrame:
    connection = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                id,
                query_text,
                retrieval_method,
                retrieved_chunk_ids,
                answer_text,
                latency_ms,
                llm_model,
                created_at
            FROM query_logs
            ORDER BY id
            """,
            connection,
        )
    finally:
        connection.close()


def export_corpus_stats() -> pd.DataFrame:
    connection = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                d.id AS document_id,
                d.title,
                d.ingested_at,
                COUNT(c.id) AS chunk_count,
                COALESCE(SUM(LENGTH(c.content)), 0) AS character_count
            FROM documents d
            LEFT JOIN chunks c
                ON c.document_id = d.id
            GROUP BY d.id, d.title
            ORDER BY d.id
            """,
            connection,
        )
    finally:
        connection.close()


def main() -> None:
    output_dir = "analytics/exports"

    query_logs = export_query_logs()
    corpus_stats = export_corpus_stats()

    query_logs.to_csv(
        f"{output_dir}/query_logs.csv",
        index=False,
    )

    corpus_stats.to_csv(
        f"{output_dir}/corpus_stats.csv",
        index=False,
    )

    print(f"Exported {len(query_logs)} query logs")
    print(f"Exported {len(corpus_stats)} documents")


if __name__ == "__main__":
    main()