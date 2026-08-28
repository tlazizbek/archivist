**[Archivist](https://github.com/tlazizbek/archivist)**

*Python · FastAPI · SQLite · scikit-learn (TF-IDF) · embeddings · uv · pytest*

I built Archivist to solve a problem I kept hitting: an answer I *knew* was
sitting somewhere in a folder of documents, with no good way to get at it.
`Ctrl+F` only works when you already know the exact words, and pasting the
question into a chatbot was worse — it answered with total confidence about
things that were nowhere in my files. Archivist is a Retrieval-Augmented
Generation pipeline that fixes both: it finds the passages that actually exist
in your documents first, then forces the LLM to answer from only those and
returns the source passages so every claim is verifiable. It's built in Python
with a FastAPI service and CLI, SQLite for storage, and runs end to end from a
single command.

The core is a hybrid retriever, and it uses two search methods because one alone
kept failing. Keyword search (TF-IDF, via scikit-learn) is literal — ask for "an
orphan girl adopted by a family on a farm" and it fixates on the word *farm*,
returning passages about slave ships while missing *Anne of Green Gables*
entirely. Embedding-based search matches meaning instead of words and fixes
that, but it blurs the exact rare terms and proper nouns that keyword search
nails cold. I ran a retrieval bake-off over 43 full-length public-domain books
from Project Gutenberg, confirmed each method won the queries the other lost, and
combined their scores so both a paraphrased question and an exact-term question
land. A logging and analytics layer tracks queries per day, latency, and which
search methods and documents get used most.
