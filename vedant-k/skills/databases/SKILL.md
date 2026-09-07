---
name: databases
description: Data storage conventions, state persistence, and audit logging.
---

# Database & State Management Guidelines

## Principles
1. **Separation of Contracts and Storage**: Pipeline outputs conform to serialization contracts (Pydantic / JSON) before persisting to DB.
2. **Immutable Audit Trails**: Every benchmark run, dataset fingerprint, and model experiment record should be append-only with execution metadata.
3. **WAL Mode & Connection Hygiene**: When using SQLite for local pipelines, enable WAL (Write-Ahead Logging) and handle concurrency cleanly.
