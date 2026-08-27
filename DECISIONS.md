# Decisions

## Chunking

- Default chunk size: 500 words.
- Default overlap: 50 words.
- The chunker uses word boundaries rather than character boundaries.
- A 10% overlap preserves context between adjacent chunks.
- These values are initial defaults and can be changed after retrieval evaluation.

## Ingestion De-duplication (Day 10)

`insert_document` returns `int | None`, not the plain `int` in the Section 9.5
manifest. Re-running ingest on an already-ingested folder should not create
duplicate rows, so the function hashes the raw text into `content_hash` (which is
`UNIQUE` in the schema) and returns `None` when a document with that hash already
exists. The CLI reads `None` as "skip this file" and prints it. This is the one
place the return type intentionally differs from the manifest, and it implements
the Day 10 decision about re-ingestion behavior.

## Batch Embedding

The manifest lists only `LLMClient.embed` (one text per call). Embedding the full
corpus one chunk at a time (8500+ chunks) is slow and makes far more HTTP requests
than necessary, so two helpers were added:

- `LLMClient.embed_batch(texts)` — embeds up to 50 chunks in a single request.
- `update_chunk_embeddings(rows)` — persists the vectors into the `embedding`
  BLOB column already defined in the schema.

`scripts/embed_corpus.py` runs this once; afterwards `SemanticRetriever.fit`
reuses the stored vectors instead of re-embedding on every startup. `embed` is
kept and still used to embed the query at search time.

## Day 14 — Retrieval Bake-Off

Run against the real corpus (43 Project Gutenberg books). Top 3 shown per
retriever; scores are cosine similarity. Reproduce with `scratch_bakeoff.py`.

### 1. Exact-term query

Query: `whale hunting harpoon`

Keyword:
1. chunk 120 — Moby Dick (the "Sperm Whale" classification passage)
2. chunk 127 — Moby Dick (porpoise/whale description)
3. chunk 8 — Moby Dick (opening whale verse)

Semantic:
1. chunk 240 — Moby Dick (fastening an extra line to the harpoon)
2. chunk 246 — Moby Dick (the struck whale rolling into view)
3. chunk 247 — Moby Dick (whether the dart is successful)

Winner: Semantic

Reason: Both retrievers correctly stayed inside Moby Dick, but keyword matched on
raw whale vocabulary and returned descriptive/classification passages, while
semantic surfaced the chunks that actually describe harpooning a whale — closer
to the intent of the query.

---

### 2. Paraphrase query

Query: `a young orphan girl adopted by a family living on a farm`

Keyword:
1. chunk 1242 — Slave ships and slaving (matched the literal word "farm")
2. chunk 2052 — Anne of Green Gables
3. chunk 7753 — A Study in Scarlet (matched "farm")

Semantic:
1. chunk 2054 — Anne of Green Gables
2. chunk 2076 — Anne of Green Gables ("an orphan and folks were at their wits' end")
3. chunk 4275 — Frankenstein

Winner: Semantic

Reason: This is the clearest split. Keyword was pulled off-topic by the literal
word "farm" and put an unrelated book first; semantic understood the description
and returned two Anne of Green Gables chunks, one of which is explicitly about
being an orphan.

---

### 3. Typo query

Query: `Sherlok Holmes detective` (Sherlock misspelled)

Keyword:
1. chunk 7731 — A Study in Scarlet (a Holmes novel)
2. chunk 3526 — The Adventures of Sherlock Holmes
3. chunk 3423 — The Adventures of Sherlock Holmes

Semantic:
1. chunk 3516 — The Adventures of Sherlock Holmes
2. chunk 3386 — The Adventures of Sherlock Holmes
3. chunk 3418 — The Adventures of Sherlock Holmes

Winner: Slight semantic

Reason: Both landed on Holmes material despite the misspelling. The typo hurt
less than expected because two of the three query words ("Holmes", "detective")
were spelled correctly, so keyword still had exact terms to match. Semantic was
more consistent, keeping all three results inside the Sherlock Holmes stories.

---

### 4. Very short query

Query: `vampire`

Keyword:
1. chunk 8413 — Dracula
2. chunk 8287 — Dracula
3. chunk 8344 — Dracula

Semantic:
1. chunk 8288 — Dracula ("take it, then, that the vampire...")
2. chunk 8413 — Dracula
3. chunk 8287 — Dracula

Winner: Tie

Reason: A single distinctive word both methods handle well — every result is
from Dracula. Semantic's top chunk is the one that most directly discusses the
vampire, but the difference is marginal.

---

### 5. Specific/technical query

Query: `What creature does the scientist assemble from dead body parts?`

Keyword:
1. chunk 3975 — Thus Spake Zarathustra (matched "body", "earth")
2. chunk 8252 — Dracula
3. chunk 4330 — Frankenstein

Semantic:
1. chunk 2437 — The war of the worlds
2. chunk 2359 — The war of the worlds
3. chunk 6609 — The Time Machine

Winner: Keyword

Reason: The surprising one. The correct answer is Frankenstein, and neither
retriever handled it cleanly. Keyword at least got Frankenstein into the top 3
via the literal word "body"; semantic over-generalized to the "science-fiction
creature" theme and returned War of the Worlds and The Time Machine, missing
Frankenstein entirely.

---

### Takeaways

- Semantic clearly wins on paraphrase (query 2) and is steadier on short or
  ambiguous queries (3, 4).
- Keyword can still win when a distinctive literal term is present, and it
  narrowly beat semantic on the hardest query (5).
- Neither is reliable on an indirect description that names none of the book's
  own vocabulary. This split is exactly what motivates the hybrid retriever in
  Day 16.

## Day 17 — LLM Error Handling

Every request sets an explicit timeout (30s for single completion and embedding
calls, 120s for the batch-embedding call, which sends up to 50 chunks at once).

A `requests.Timeout` is caught and re-raised as a RuntimeError with a clear
message, so a slow or unresponsive provider fails fast instead of hanging the
request indefinitely.

HTTP 429 rate-limit responses are handled the same way — raised as a RuntimeError.
The client does not retry automatically because this project does not yet need
retry or exponential-backoff infrastructure.