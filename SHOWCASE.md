## [Archivist](https://github.com/tlazizbek/archivist)

*Python · FastAPI · SQLite · scikit-learn (TF-IDF) · embeddings · uv*

I kept losing answers I *knew* were sitting somewhere in a folder of documents.
`Ctrl+F` only helps when you already know the exact words — the one thing you
never have when you're searching — and pasting the question into a chatbot was
worse, because it answered with total confidence about things that were nowhere
in my files. Archivist is my answer to both failures: a Retrieval-Augmented
Generation pipeline that finds the passages that actually exist in your
documents first, then forces the LLM to answer from only those and returns the
source passages so you can verify every claim. I built it against 43 full-length
public-domain books from Project Gutenberg, so the retrieval had to hold up on
real, messy text rather than a toy corpus.

It uses two search methods because one alone kept failing, and they failed in
opposite ways. Keyword search (TF-IDF) is literal: ask for "a young orphan girl
adopted by a family on a farm" and it fixates on the word *farm*, surfacing
passages about slave ships while missing *Anne of Green Gables* entirely.
Embedding search fixes that by matching meaning instead of words — but it blurs
exact, rare terms and proper nouns that keyword search nails cold. I ran a
bake-off on the real corpus, watched each method win the queries the other lost,
and settled on a hybrid retriever that scores both and combines them, so a
question phrased in your own words and a question with one exact term both land.
Archivist runs from a single command as a CLI or a FastAPI service, and logs
every query into a small analytics layer.
