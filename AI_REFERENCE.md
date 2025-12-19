# AI Reference

This file tracks the project structure, roadmap, and conventions for the SAP (Semantic Alignment Protocol) local-first service.
Keep this in sync with `README.md` whenever the structure or scope changes.

## Project Summary
SAP is a local-first alignment layer that ingests artifacts, builds capsules (goals/constraints/decisions/glossary/etc), and analyzes drafts for gaps, mismatches, and lens-specific clarity needs. It exposes a minimal FastAPI surface for ingestion, retrieval, and draft analysis, with optional local LLM rendering.

## Roadmap (from docs)
- Milestone A: Local memory + retrieval (SQLite schema, FTS, embeddings, ingest pipeline).
- Milestone B: Gap + mismatch analysis (glossary/exposure ledger, draft analyze fast-pass).
- Milestone C: Multi-lens rendering (LLM router + render pipeline, optional LLM).
- Milestone D: After-receive explain + profiles (sender lens card, assumption signatures).
- Milestone E: Debate engine (idea clusters, contradictions, discriminating tests).
- Milestone F: Publish + federation (redaction, signing, CRDT/manifest sync).

## Current Status
- Scaffolding started for core models, SQLite migrations, ingest pipeline, retrieval, and draft analysis/render endpoints.

## Source Tree (src)
```text
src/
  sap_api/
    app.py              # FastAPI app entrypoint + router registration
    deps.py             # DB dependency wiring
    routes/
      health.py         # /v1/health
      workspace.py      # /v1/workspace/create, /v1/workspace/{id}
      ingest.py         # /v1/artifact/ingest
      capsule.py        # /v1/capsule/query
      draft.py          # /v1/draft/analyze, /v1/draft/render
  sap_core/
    domain/models.py    # Enums + Pydantic domain/request/response models
    retrieval/retrieve.py
    scoring/scoring.py
    prompts/templates.py
    pipelines/
      ingest.py         # Artifact ingest + chunking
      draft_analyze.py  # Fast-pass gap/mismatch analysis
      draft_render.py   # Render pipeline (LLM optional)
  sap_models/
    router.py           # LLM routing policy
    embedder.py         # Optional sentence-transformers embedder
    llm.py              # Optional llama.cpp wrapper
  sap_store/
    sqlite/
      db.py             # SQLite connection helpers
      migrate.py        # Migration runner
      migrations/
        0001_init.sql
        0002_fts.sql
        0003_jobs.sql
  sap_workers/
    worker.py           # Minimal job runner stub
```

## Key Concepts (alignment to docs)
- Capsules are the only publishable boundary objects; raw artifacts stay local.
- Retrieval uses guardrail capsules (goals/constraints/decisions) plus FTS/embeddings.
- Draft analysis is deterministic (no-LLM) in the fast pass; LLM rendering is optional and gated.
