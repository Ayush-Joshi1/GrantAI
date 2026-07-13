## `src/models`

This folder exists to match common backend conventions (**models**).

Recommended usage:
- **Domain models**: `src/domain/*` (entities/value objects).
- **Persistence models** (ORM tables): `src/infrastructure/persistence/`.
- **API DTO models**: `src/api/v1/schemas/`.

`src/models/` is intentionally reserved for shared model definitions that don’t cleanly fit the above,
but prefer the three-layer split to avoid mixing concerns.

