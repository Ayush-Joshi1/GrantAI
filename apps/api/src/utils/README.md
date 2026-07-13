## `src/utils`

This folder exists to match common backend conventions (**utils**).

Guideline:
- Only put **pure** helpers here (no network/DB/IBM calls).
- Cross-cutting “system” utilities belong in `src/core/` (logging, config, errors, security).

