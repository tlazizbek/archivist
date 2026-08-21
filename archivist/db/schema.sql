CREATE TABLE documents (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT NOT NULL,
    source_path   TEXT NOT NULL,
    source_type   TEXT NOT NULL,
    content_hash  TEXT NOT NULL UNIQUE,
    ingested_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chunks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id   INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index   INTEGER NOT NULL,
    content       TEXT NOT NULL,
    token_count   INTEGER,
    embedding     BLOB,
    UNIQUE(document_id, chunk_index)
);

CREATE TABLE query_logs (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text            TEXT NOT NULL,
    retrieval_method      TEXT NOT NULL,
    retrieved_chunk_ids   TEXT,
    answer_text           TEXT,
    latency_ms            INTEGER,
    llm_model             TEXT,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE query_feedback (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    query_log_id    INTEGER NOT NULL REFERENCES query_logs(id),
    rating          INTEGER,
    note            TEXT
);