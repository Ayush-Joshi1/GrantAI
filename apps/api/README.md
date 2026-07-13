# `apps/api`

FastAPI backend following Clean Architecture:

- **Delivery**: `src/api/` (routers, schemas, middleware)
- **Use-cases**: `src/application/` (orchestrates business flows and external ports)
- **Domain**: `src/domain/` (entities and rules; framework-independent)
- **Infrastructure**: `src/infrastructure/` (DB, FAISS, IBM watsonx adapters, queues, storage)
- **Cross-cutting**: `src/core/` (config, logging, errors, security, observability)
- **Prompts**: `src/prompts/` (versionable prompt templates)

## Local development startup

From the repository root, run:

```bash
python apps/api/run.py
```

This helper ensures the backend imports `src/` and `backend/` packages correctly and starts Uvicorn with `API_HOST`, `API_PORT`, and `LOG_LEVEL` from environment variables.

