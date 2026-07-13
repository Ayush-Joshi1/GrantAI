# `apps/workers`

Background workers for long-running operations:
- proposal generation
- ingestion + parsing + embedding
- index rebuilds

This keeps the API responsive and supports scaling independently from the HTTP layer.

