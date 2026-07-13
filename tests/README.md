RAG End-to-End Tests

This folder contains a simple end-to-end test harness for the RAG pipeline.

Setup

Install dependencies (recommended in virtualenv):

```bash
pip install -r requirements.txt
# or at minimum:
pip install faiss-cpu sentence-transformers langchain
```

Run the test

```bash
python -m tests.rag_e2e_test
```

What it does

- Loads documents from `tests/data/`
- Splits documents into chunks
- Generates embeddings via Sentence Transformers
- Creates/updates a FAISS index (default path: `data/rag/faiss.index`)
- Runs a set of sample queries
- Prints retrieved chunks, metadata, similarity scores, and timings

Notes

- This is a diagnostic utility only; do not connect any LLM or IBM Granite when running.
- If your environment lacks FAISS or SentenceTransformers, install them or run in an environment that supports these packages.
