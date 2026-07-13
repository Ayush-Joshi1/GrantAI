## `core/config`

Centralized configuration layer.

Why it exists:
- Keeps secrets and environment parsing in one place.
- Provides typed settings objects to the rest of the system.
- Enables clean dependency injection (application depends on interfaces, not env vars).

