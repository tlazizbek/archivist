import pandas as pd

from archivist.db.database import get_connection


def export_query_logs() -> pd.DataFrame:
    connection = get_connection()

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

def export_corpus_stats() -> pd.DataFrame:
    connection = get_connection()

    return pd.read_sql_query(
        """
        SELECT
            d.id AS document_id,
            d.title,
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