## `src/services`

This folder exists to match common backend conventions (**services**).

In this repo’s Clean Architecture:
- Use-cases (“application services”) live in `src/application/`.
- External adapters (IBM watsonx, DB, FAISS, COS, queues) live in `src/infrastructure/`.
- `src/services/` can hold thin service facades when you want a simpler integration surface for routes
  while keeping domain logic inside `src/application/` and `src/domain/`.

