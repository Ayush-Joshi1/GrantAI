# Diagram Specifications for GrantAI

These specifications describe the diagrams that should accompany GrantAI documentation.

## System Architecture Diagram

Include:
- Frontend (`apps/web/`) as the user interface.
- Backend (`apps/api/`) as the FastAPI service.
- RAG infrastructure (`backend/rag/`) for retrieval, embeddings, and FAISS.
- IBM integrations: Granite, Assistant, Orchestrate.
- Environment configuration and `.env` variables.
- Data flow from user request to IA response.

## Workflow Flow Diagram

Include:
- User request entering the frontend.
- API request to FastAPI route.
- ChatService intent detection and workflow invocation.
- WorkflowCoordinator stages: recommendation, eligibility, proposal, deadline, notification.
- Prompt Builders generating tasks.
- RAGAnswerService retrieval and Granite generation.
- Response aggregation and return to frontend.

## Component Diagram

Include:
- `apps/api/src/api` routes and schemas.
- `apps/api/src/application` services.
- `apps/api/src/infrastructure/ibm` adapters.
- `backend/rag` embedding and retriever components.
- Prompt builder modules.
- Dependency injection container and service providers.

## Data Flow Diagram

Include:
- Request payloads and response payloads.
- RAG retrieval from vector store.
- IBM Granite response path.
- Assistant and Orchestrate fallback/execution paths.
- Source citations and grounding output.

## Notes
- These diagram specifications are suitable for manual drawing or slide creation.
- Use the repository structure and service names exactly as written.
