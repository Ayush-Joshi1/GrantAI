# Grant Agent (IBM Hackathon)

AI-powered platform to help Indian startups discover government grants, check eligibility, chat with an AI assistant, and generate grant proposals.

This repository is structured for **Clean Architecture**, **SOLID**, and future integration of **RAG**, **IBM watsonx.ai Granite**, **watsonx Assistant**, **watsonx Orchestrate**, **ML models**, and **multiple AI agents**.

## Repo layout (why each folder exists)

### `apps/` (deployable applications)
- **`apps/web/`**: React + Vite + Tailwind frontend (component-based, feature-oriented).
  - **`public/`**: Static assets served as-is (favicons, robots.txt).
  - **`src/app/`**: App shell (router, providers, layout, global error boundaries).
  - **`src/features/`**: Feature modules (discover-grants, eligibility, chat, proposal-builder). Keeps domain UI cohesive and scalable.
  - **`src/components/`**: Shared “glue” components used across multiple features (thin wrappers, composed UI).
  - **`src/design-system/`**: Tokens + primitives + styling conventions (Tailwind config alignment).
  - **`src/services/`**: API client, telemetry, feature flags, auth integration.
  - **`src/state/`**: Server-state cache and minimal global state (e.g., React Query, Zustand).
  - **`src/hooks/`**: Shared React hooks (typed, reusable).
  - **`src/styles/`**: Global styles (Tailwind base imports, theme extensions).
  - **`src/types/`**: Frontend-only types (or generated types from OpenAPI in the future).
  - **`src/utils/`**: Pure utilities (formatters, validators).

- **`apps/api/`**: FastAPI backend (HTTP delivery + use-cases + adapters).
  - **`src/api/`**: Delivery layer (routers/controllers, DTO schemas, middleware). No business logic.
    - **`v1/routes/`**: Versioned routers per bounded context (grants, eligibility, chat, proposals, admin).
    - **`v1/schemas/`**: Request/response DTOs (Pydantic) that define the API contract.
    - **`middleware/`**: Cross-cutting HTTP concerns (correlation IDs, auth, rate limiting hooks).
  - **`src/application/`**: Use-cases (orchestrate domain + ports). This is where “what the system does” lives.
  - **`src/domain/`**: Pure business rules (entities, value objects, domain services). No framework imports.
  - **`src/infrastructure/`**: Adapters/implementations for external systems (DB, vector store, IBM services, queues).
    - **`ibm/`**: watsonx.ai Granite client, Assistant tool adapters, Orchestrate workflow adapters.
    - **`persistence/`**: SQL/ORM repositories (Postgres), migrations strategy (future).
    - **`vectorstore/`**: FAISS index build/load/query adapters.
    - **`queues/`**: Background job queue adapters (Celery/RQ/Arq), retry policies, idempotency.
    - **`storage/`**: Object storage adapters (IBM Cloud Object Storage) for docs/exports/index artifacts.
  - **`src/core/`**: Shared cross-cutting modules used everywhere (config, logging, errors, security, observability).
  - **`src/prompts/`**: Prompt templates (system prompts, Granite prompts, RAG answer templates). Versionable and testable.
  - **`tests/`**: Unit/integration tests (use-case tests first; API tests second).

- **`apps/workers/`**: Background workers for long-running tasks (proposal generation, ingestion, embedding).
  - **`src/jobs/`**: Atomic job handlers (generate proposal section, parse pdf, embed chunks).
  - **`src/workflows/`**: Multi-step pipelines (can mirror Orchestrate workflows or run locally).

### `packages/` (shared libraries)
- **`packages/shared-types/`**: Shared contracts/types between web and api (future: OpenAPI-generated TS types).
- **`packages/ui-kit/`**: Reusable UI components (design system implementation), independent of app routing.
- **`packages/python-shared/`**: Shared Python utilities (typed errors, logging helpers, config helpers).

### `docs/` (documentation that scales)
- **`docs/architecture/`**: Architecture diagrams (C4), flow docs, threat model notes.
- **`docs/adr/`**: Architecture Decision Records (why we chose X over Y).
- **`docs/api/`**: OpenAPI exports, Postman collections, example payloads.

### `infra/` (deployment & operations)
- **`infra/pipelines/`**: CI/CD definitions (GitHub Actions, Tekton, etc.).
- **`infra/terraform/`**: IBM Cloud infrastructure as code (optional).
- **`infra/helm/`**: Kubernetes packaging (optional).

### `scripts/` (developer productivity)
- Local scripts for ingestion runs, index rebuilds, data validation, and environment bootstrapping.

## Environment
- Copy `.env.example` to `.env` and fill values.

## Documentation assets
- Architecture notes: `docs/architecture/README.md`
- API notes: `docs/api/README.md`
- Submission checklist: `docs/submission_checklist.md`
- Demo outline: `docs/demo_outline.md`
- Diagram specifications: `docs/diagram_specifications.md`

## Next steps
- For final delivery, review `docs/submission_checklist.md` and perform any manual IBM Cloud configuration required for live service validation.

