# Architecture Notes

## Backend flow

The backend follows a thin transport layer over a small application layer:

1. FastAPI routes accept HTTP requests and map them to application services.
2. Application services orchestrate prompt construction and reuse the shared RAG answer service.
3. The shared RAG answer service performs retrieval, prompt building, and Granite generation through a single grounded path.
4. The retriever and vector store layer provide source-backed context for the agents.

## Key boundaries

- Delivery layer: API routes and schemas under apps/api/src/api
- Application layer: services and orchestration under apps/api/src/application
- Infrastructure layer: IBM Granite, vector store, and retriever adapters under apps/api/src/infrastructure
- Prompt layer: prompt builders under apps/api/src/prompts

## Current Sprint 2 shape

- Five agent services expose recommendation, eligibility, proposal, deadline, and notification workflows.
- Prompt builders remain isolated from routing logic.
- The shared RAG answer service is the single production path for retrieval and Granite generation.
