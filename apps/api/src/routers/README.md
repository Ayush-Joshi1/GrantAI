## `src/routers`

This folder exists to match common FastAPI conventions (**routers**).

In this repo’s Clean Architecture:
- The “real” HTTP layer lives in `src/api/v1/routes/` (versioned routers).
- `src/routers/` is reserved for future non-versioned or shared routing composition if needed.

