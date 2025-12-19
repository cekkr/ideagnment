# Milestone A Checklist: Local Memory + Retrieval

Target scope: SQLite schema, FTS, embeddings, ingest pipeline, and capsule retrieval.

- [x] SQLite base schema for workspaces, artifacts, chunks, capsules, exposure, and policy.
- [x] FTS virtual tables for chunks and capsules.
- [x] Migration runner and versioned migrations in `src/sap_store/sqlite/migrations`.
- [x] Artifact ingest pipeline with chunking and FTS indexing.
- [x] Capsule retrieval bundle (guardrails + FTS lookup).
- [x] `GET /v1/capsule/query` endpoint.
- [ ] Embedding generation hooked to ingest and stored in `embedding`.
- [ ] Vector retrieval wired into `retrieve_bundle` via `query_vec`.
- [ ] Basic fixture dataset for retrieval checks.
- [ ] Minimal retrieval tests (FTS hit + guardrail inclusion).
- [ ] Document local DB location and reset/cleanup steps.
