# Decisions

## Chunking

- Default chunk size: 500 words.
- Default overlap: 50 words.
- The chunker uses word boundaries rather than character boundaries.
- A 10% overlap preserves context between adjacent chunks.
- These values are initial defaults and can be changed after retrieval evaluation.