# Decisions

## Chunking

- Default chunk size: 500 words.
- Default overlap: 50 words.
- The chunker uses word boundaries rather than character boundaries.
- A 10% overlap preserves context between adjacent chunks.
- These values are initial defaults and can be changed after retrieval evaluation.

## Day 14 — Retrieval Bake-Off

### 1. Exact-term query

Query: `organization membership`

Keyword:
1. chunk 5 — About organization membership
2. chunk 15 — Concepts for account and profile
3. chunk 6 — Your organization's profile

Semantic:
1. chunk 5 — About organization membership
2. chunk 6 — Your organization's profile
3. chunk 18 — Email/account access content

Winner: Keyword

Reason: Both retrievers found the correct organization membership chunk first, but keyword retrieval produced a more focused top 3 with fewer unrelated results.

---

### 2. Paraphrase query

Query: `How can I become part of an organization?`

Keyword:
1. chunk 5 — About organization membership
2. chunk 17 — Personal account management
3. chunk 6 — Your organization's profile

Semantic:
1. chunk 5 — About organization membership
2. chunk 6 — Your organization's profile
3. chunk 20 — Contributions on your profile

Winner: Semantic

Reason: Both methods found the correct membership chunk first, but semantic retrieval ranked another organization-related chunk second and handled the paraphrased wording well.

---

### 3. Typo query

Query: `organizatoin membership`

Keyword:
1. chunk 5 — About organization membership
2. chunk 15 — Concepts for account and profile
3. chunk 17 — Personal account management

Semantic:
1. chunk 5 — About organization membership
2. chunk 6 — Your organization's profile
3. chunk 17 — Personal account management

Winner: Semantic

Reason: Semantic retrieval remained focused on organization-related content despite the misspelled word, while keyword retrieval returned more general account content.

---

### 4. Very short query

Query: `username`

Keyword:
1. chunk 3 — Username changes
2. chunk 4 — Username reference content
3. chunk 15 — Concepts for account and profile

Semantic:
1. chunk 3 — Username changes
2. chunk 19 — Personal account/profile content
3. chunk 15 — Concepts for account and profile

Winner: Keyword

Reason: The exact keyword strongly identifies the username documentation, and keyword retrieval produced a highly relevant second result containing username-related content.

---

### 5. Specific/technical query

Query: `How can I change the email address associated with my GitHub account?`

Keyword:
1. chunk 14 — Email/account verification content
2. chunk 13 — Email addresses
3. chunk 18 — Email/account access content

Semantic:
1. chunk 14 — Email/account verification content
2. chunk 13 — Email addresses
3. chunk 18 — Email/account access content

Winner: Tie

Reason: Both retrievers returned the same three most relevant chunks in the same order, showing that both methods handled this specific technical query well.

## Day 17 — LLM Error Handling

The LLM client uses a 30-second request timeout.

Timeouts raise a RuntimeError instead of waiting indefinitely.

HTTP 429 rate-limit responses also raise a RuntimeError. The client does not retry automatically because this project does not yet need retry or exponential-backoff infrastructure.