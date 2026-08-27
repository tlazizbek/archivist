# Archivist

A backend service that turns a folder of plain-text documents into a searchable,
question-answering knowledge base. It ingests `.txt`/`.md` files, splits them into
overlapping chunks, indexes them for both keyword and semantic search, and answers
natural-language questions with an LLM that is instructed to speak only from the
retrieved text. Every query is logged, and those logs feed a small analytics layer
and a Power BI dashboard.

This is my Boot.dev backend + AI capstone. The development corpus is 43 public-domain
books from Project Gutenberg.

## Architecture

The system is six layers:

1. **Ingestion** (`archivist/ingestion/`) — read files, clean the text, split into chunks.
2. **Storage** (`archivist/db/`) — SQLite: `documents`, `chunks`, `query_logs` (+ `query_feedback` for later).
3. **Retrieval** (`archivist/retrieval/`) — a TF-IDF keyword retriever, an embedding-based
   semantic retriever, and a hybrid retriever that merges the two.
4. **Generation** (`archivist/generation/`) — build a grounded prompt from the retrieved
   chunks and call the LLM over HTTP.
5. **Interface** (`archivist/cli.py`, `archivist/api/`) — a CLI `ingest` command and a
   FastAPI service (`/ingest`, `/query`, `/health`).
6. **Analytics** (`analytics/`) — pull the logs with Pandas, export CSVs, and chart them in Power BI.

## Requirements

- Python 3.13+
- An LLM provider with an OpenAI-compatible `/embeddings` and `/chat/completions` API
  (developed against OpenRouter's free tier).

## Setup

This project uses [uv](https://docs.astral.sh/uv/). With uv:

```bash
uv sync
```

Or with pip and a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then create a `.env` from the example and fill in your provider details:

```bash
cp .env.example .env
```

```
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-provider/api/v1
DB_PATH=./archivist.db
```

## Usage

All commands assume you are in the project root. Prefix with `uv run` (or activate the venv first).

**Ingest a folder.** This creates the database on first run, cleans and chunks every
file, and skips any file already ingested:

```bash
uv run python -m archivist.cli ingest data/raw
```

**Generate embeddings** for the ingested chunks (needed for semantic and hybrid search).
It embeds in batches and stores the vectors in the database, so it only runs once per corpus:

```bash
uv run python -m scripts.embed_corpus
```

**Run the API:**

```bash
uv run uvicorn archivist.api.app:app --reload
```

```bash
# liveness
curl http://127.0.0.1:8000/health

# ask a question (method: keyword | semantic | hybrid; defaults to hybrid)
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the characteristics of sperm whales?", "method": "hybrid"}'
```

`/query` returns the answer, the source chunks it was built from, and the latency in
milliseconds, and writes a row to `query_logs`.

**Run the tests:**

```bash
uv run pytest
```

**Analytics.** Export the logs and corpus stats to CSV, or run the notebook end to end:

```bash
uv run python -m analytics.export           # writes analytics/exports/*.csv
```

`analytics/notebooks/analysis.ipynb` computes queries per day, average and p95 latency,
retrieval-method usage, and the most-retrieved documents, and exports the CSVs the Power BI
dashboard reads (`dashboard/archivist.pbix`).

## Key design decisions

The full reasoning, including the search comparison I ran, is in
[DECISIONS.md](DECISIONS.md). In plain terms:

1. **How documents get split up.** Long documents are cut into smaller pieces of about
   500 words, and each piece overlaps the one before it by about 50 words. Small pieces
   are quick to search, and the overlap means an idea that lands right on the line between
   two pieces still shows up in both, so it doesn't get lost.
2. **How the search works.** The system looks for relevant pieces two ways at once: one
   matches the exact words in your question, the other matches the meaning even when you
   word things differently. Neither is better on its own — exact words are good for names
   and specific terms, meaning is good for rephrased questions — so the system uses both
   and ranks the combined results. To stay fast, it works out the meaning of every piece
   once and saves it, instead of redoing that every time.
3. **Answers stay grounded, and problems are handled.** The model is told to answer only
   from the pieces the system found, and to say so when the answer isn't there — so it
   doesn't make things up. If the outside AI service is slow or busy, the system stops
   waiting after a set time and reports a clear error instead of freezing.

## Project status

MVP through the analytics layer. Stretch goals (reranking, an agentic loop, an evaluation
harness) are scoped in the plan but not yet built. `archivist/retrieval/reranker.py` and
`archivist/agent/loop.py` are placeholders for that work.
