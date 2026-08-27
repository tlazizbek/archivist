# Archivist

> Point it at a folder of documents and ask them questions in plain English.

**Archivist** turns a pile of plain-text files into a knowledge base you can talk to.
Drop in your `.txt` and `.md` files, ask a question in your own words, and get a
straight answer that is built only from what your documents actually say, with the
source passages to back it up.

Under the hood it is a complete **Retrieval-Augmented Generation (RAG)** pipeline:
ingestion, storage, hybrid search, grounded answer generation, and an analytics layer,
all runnable from a single command.

## Description

Ask a question and Archivist:

1. **Finds** the most relevant passages in your documents, using two kinds of search at
   once: exact-word matching (TF-IDF) and meaning-based matching (embeddings).
2. **Answers** from those passages with an LLM that is instructed to use only what it
   found, and to say so when the answer is not there, so it does not make things up.
3. **Shows its work** by returning the exact passages it used as sources.
4. **Logs** every question, which feeds a small analytics layer (queries per day,
   latency, most-used search methods, most-retrieved documents).

It ships with a one-command launcher, a terminal CLI, and a FastAPI web service.

## Motivation

This is my **Boot.dev backend + AI capstone**. I wanted to build a real
Retrieval-Augmented Generation system end to end rather than glue together a demo:
document ingestion and chunking, a proper storage layer, more than one retrieval
strategy compared head to head, grounded generation with sensible failure handling,
and analytics on top of real usage.

To keep it honest, I built and tested it on **43 public-domain books from Project
Gutenberg**, so the search has to work over real, messy, full-length text.

## Quick Start

**Requirements**

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- An LLM provider with an OpenAI-compatible `/embeddings` and `/chat/completions` API
  (built against OpenRouter's free tier)

**Get running in three steps**

```bash
# 1. Install dependencies
uv sync

# 2. Add your provider details (edit .env and fill in LLM_API_KEY and LLM_BASE_URL)
cp .env.example .env

# 3. Set up everything and launch, in one command
uv run archivist start --docs data/raw
```

When it is ready, Archivist prints a link (for example `http://127.0.0.1:8000/docs`).
**Open that link in your browser to ask questions**, no terminal or `curl` required.
Press `Ctrl+C` to stop it.

On later runs your documents are already added, so you can just:

```bash
uv run archivist start
```

## Usage

The `start` command above bundles the whole workflow. If you would rather run one stage
at a time, or wire Archivist into something else, each step is also available on its own.
Run these from the project root with `uv run` in front (or activate the venv first).

### Add documents

The first run creates the database. Text is cleaned and split into overlapping pieces,
and any file that was already added is skipped.

```bash
uv run archivist ingest data/raw
```

### Build the search index

Work out the meaning (embedding) of each piece so semantic and hybrid search can use it.
This runs in batches and saves the result, so you only do it once per set of documents.

```bash
uv run python -m scripts.embed_corpus
```

### Run the web service

```bash
uv run uvicorn archivist.api.app:app --reload
```

Then, for developers, hit the API directly:

```bash
# is it alive?
curl http://127.0.0.1:8000/health

# ask a question (method: keyword | semantic | hybrid; defaults to hybrid)
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the characteristics of sperm whales?", "method": "hybrid"}'
```

The `/query` response contains the answer, the passages used as sources, and the
latency in milliseconds. Every question is saved to `query_logs`.

### Run the tests

```bash
uv run pytest
```

### Analytics

Export the logs and corpus stats as CSVs, or run the notebook from top to bottom.

```bash
uv run python -m analytics.export   # writes analytics/exports/*.csv
```

`analytics/notebooks/analysis.ipynb` works out queries per day, average and p95 latency,
which search methods were used, and the most-retrieved documents.

## How it works

The system is built in six layers:

| Layer | Location | What it does |
| --- | --- | --- |
| **Ingestion** | `archivist/ingestion/` | Read files, clean the text, split into overlapping pieces. |
| **Storage** | `archivist/db/` | SQLite with `documents`, `chunks`, and `query_logs` tables. |
| **Retrieval** | `archivist/retrieval/` | Keyword (TF-IDF), semantic (embeddings), and a hybrid that merges both. |
| **Generation** | `archivist/generation/` | Build the prompt from the retrieved pieces and call the LLM. |
| **Interface** | `archivist/cli.py`, `archivist/api/` | The `start` and `ingest` commands, plus the FastAPI service. |
| **Analytics** | `analytics/` | Pull the logs with Pandas, export CSVs, analyze in a notebook. |

### Key design decisions

The full reasoning, including the search comparison I ran, is in
[DECISIONS.md](DECISIONS.md). In short:

1. **How documents get split up.** Long documents are cut into pieces of about 500 words,
   each overlapping the previous one by about 50 words. Small pieces are quick to search,
   and the overlap keeps an idea that falls on the boundary between two pieces from getting
   lost.
2. **How the search works.** Archivist retrieves two ways at once: exact words are good for
   names and specific terms, meaning is good for rephrased questions. Neither wins alone, so
   it ranks the combined results. To stay fast, each piece is embedded once and stored,
   instead of being re-embedded on every query.
3. **Answers stay grounded, and failures are handled.** The model is told to answer only
   from the retrieved pieces and to admit when the answer is not there. If the LLM provider
   is slow or busy, Archivist stops waiting after a timeout and returns a clear error instead
   of hanging.

## Project status

The core project is complete through the analytics layer. The stretch goals (reranking, an
agent loop, and an evaluation harness) are planned but not built yet;
`archivist/retrieval/reranker.py` and `archivist/agent/loop.py` are empty placeholders.

## Contributing

This is a personal capstone project, so it is not looking for feature contributions.
Bug reports and suggestions are welcome:

1. Open an issue describing the problem or idea.
2. If you want to send a fix, fork the repo and create a branch.
3. Make sure the tests pass with `uv run pytest`.
4. Open a pull request that explains what changed and why.
