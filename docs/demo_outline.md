# GrantAI Demo Outline

## Objective
Demonstrate how GrantAI supports founders in discovering grants, checking eligibility, generating proposal drafts, and receiving notification guidance.

## Walkthrough steps
1. Open the GrantAI frontend.
2. Show the startup profile input or chat interface.
3. Submit a founder query or startup profile.
4. View grant recommendation results.
5. Run eligibility analysis for a selected grant.
6. Generate a proposal draft.
7. Generate deadline and notification guidance.
8. Highlight source citations and grounded response behavior.
9. Open the health endpoint and API docs to confirm the backend is available.

## Key talking points
- Clean Architecture separation between frontend, API, application services, and IBM adapters.
- Shared RAG answer service and prompt builder reuse.
- IBM Granite for grounded generative output.
- watsonx Assistant fallback and chat experience.
- watsonx Orchestrate workflow support for unified automation.

## Notes
- The backend exposes `/api/v1/docs` for API exploration.
- The frontend uses `VITE_API_BASE_URL=/api/v1`.
- Live IBM credentials are required for full runtime behavior.
