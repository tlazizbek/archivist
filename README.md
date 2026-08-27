# Archivist

Archivist turns a folder of plain-text documents into a searchable, question-answering
knowledge base. It reads `.txt` and `.md` files and splits them into small overlapping
pieces. It then indexes those pieces for two kinds of search: matching the exact words, and
matching the meaning. When you ask a question, it finds the most relevant pieces and answers
from them with an LLM that is told to use only what it found. Every question is logged, and
those logs feed a small analytics layer.

This is my Boot.dev backend + AI capstone. I built it on 43 public-domain books from
Project Gutenberg.

## Architecture

The system has six layers:

1. **Ingestion** (`archivist/ingestion/`) — read the files, clean the text, and split it into pieces.
2. **Storage** (`archivist/db/`) — an SQLite database with three tables: `documents`, `chunks`,
   and `query_logs` (`query_feedback` is for later).
3. **Retrieval** (`archivist/retrieval/`) — three searchers: keyword (TF-IDF), semantic
   (embeddings), and a hybrid that merges the two.
4. **Generation** (`archivist/generation/`) — build the prompt from the pieces that were found
   and send it to the LLM.
5. **Interface** (`archivist/cli.py`, `archivist/api/`) — an `ingest` command for the terminal
   and a FastAPI service with `/ingest`, `/query`, and `/health`.
6. **Analytics** (`analytics/`) — pull the logs with Pandas, save them as CSVs, and analyze them
   in a notebook.

## Requirements

- Python 3.13+
- An LLM provider with an OpenAI-compatible `/embeddings` and `/chat/completions` API
  (built against OpenRouter's free tier).

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

Then copy the example `.env` and fill in your provider details:

```bash
cp .env.example .env
```

```
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-provider/api/v1
DB_PATH=./archivist.db
```

## Usage

Run these from the project root. Put `uv run` in front of each one (or activate the venv first).

**Add a folder of documents.** The first run creates the database. It cleans and splits every
file, and skips any file that was already added:

```bash
uv run python -m archivist.cli ingest data/raw
```

**Work out the meaning of each piece** so that semantic and hybrid search can use it. This runs
in batches and saves the results in the database, so you only need to run it once per set of
documents:

```bash
uv run python -m scripts.embed_corpus
```

**Run the API:**

```bash
uv run uvicorn archivist.api.app:app --reload
```

```bash
# is it alive?
curl http://127.0.0.1:8000/health

# ask a question (method: keyword | semantic | hybrid; defaults to hybrid)
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the characteristics of sperm whales?", "method": "hybrid"}'
```

The `/query` response has the answer, the pieces it used as sources, and how long it took in
milliseconds. Each question is also saved to `query_logs`.

**Run the tests:**

```bash
uv run pytest
```

**Analytics.** Save the logs and corpus stats as CSVs, or run the notebook from top to bottom:

```bash
uv run python -m analytics.export           # writes analytics/exports/*.csv
```

`analytics/notebooks/analysis.ipynb` works out queries per day, average and p95 latency, which
search methods were used, and the most-retrieved documents, saving the results as CSVs.

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

The core project is done through the analytics layer. The stretch goals — reranking, an agent
loop, and an evaluation harness — are planned but not built yet. `archivist/retrieval/reranker.py`
and `archivist/agent/loop.py` are empty placeholders for them.
