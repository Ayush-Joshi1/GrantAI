# `src/prompts`

Prompt templates are treated as **versioned assets**:
- **`system/`**: system + safety prompts (tone, constraints, policy).
- **`granite/`**: IBM Granite prompts (drafting, summarization, extraction).
- **`rag/`**: RAG answer templates and citation formatting prompts.

Why it exists:
- Enables prompt iteration without mixing with code.
- Supports prompt testing and rollback.
- Makes it easy to swap providers (Granite now, others later) without rewriting use-cases.

