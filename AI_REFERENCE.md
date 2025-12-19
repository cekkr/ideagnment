# AI Reference

This file tracks the project structure, roadmap, and conventions for the SAP (Semantic Alignment Protocol) local-first service.
Keep this in sync with `README.md` whenever the structure or scope changes.

## Project Summary
SAP is a local-first alignment layer that ingests artifacts, builds capsules (goals/constraints/decisions/glossary/etc), and analyzes drafts for gaps, mismatches, and lens-specific clarity needs. It exposes a minimal FastAPI surface for ingestion, retrieval, and draft analysis, with optional local LLM rendering.

Data possession is a first-class concern: skill claims/evidence default to private scope, and institution views must not reveal private evidence. Decentralized deployment is expected (each instance controls its own local data), with only explicitly shared artifacts/capsules exposed.

## Docs
- `docs/semanticAlignmentProtocol-roadmap.md` (full roadmap and spec)
- `docs/main-prompt-concept.md` (origin concept prompt)
- `docs/getting-started.md` (end-to-end walkthrough)
- `docs/milestone-a-checklist.md` (implementation tracker)

## Examples
- `examples/mock_messaging/index.html` (mock messaging web UI reference)
- `examples/mock_messaging/server.py` (demo server + seeded data for API-backed results)

## Roadmap (from docs)
- Milestone A: Local memory + retrieval (SQLite schema, FTS, embeddings, ingest pipeline).
- Milestone B: Gap + mismatch analysis (glossary/exposure ledger, draft analyze fast-pass).
- Milestone C: Multi-lens rendering (LLM router + render pipeline, optional LLM).
- Milestone D: After-receive explain + profiles (sender lens card, assumption signatures).
- Milestone E: Debate engine (idea clusters, contradictions, discriminating tests).
- Milestone F: Publish + federation (redaction, signing, CRDT/manifest sync).

## Current Status
- Scaffolding started for core models, SQLite migrations, ingest pipeline, retrieval, and draft analysis/render endpoints.
- Added skills reporting/earning with privacy partitioning and institution-safe views.
- Added dynamic model catalog/selector primitives for local compute and cost-aware routing.
- Skills endpoints enforce identity via `X-Actor-Id` (and `X-Org-Id` for institution views).
- Model catalog is loaded from `config/models.json` (override with `SAP_MODEL_CATALOG_PATH`) and can be edited at runtime.
- Added a mock messaging web demo for circle-based alignment flows at `examples/mock_messaging/index.html`.
- Added a demo server for the mock messaging UI at `examples/mock_messaging/server.py`.

## Demo Reference: Mock Messaging Web System
- Location: `examples/mock_messaging/index.html`.
- Server: `examples/mock_messaging/server.py` (serves the UI and seeds demo data).
- Purpose: demonstrate circle membership, skills/vision changes over time, and alignment workflows in a messaging UI.
- Compose flow: drafts call `/v1/draft/analyze` and `/v1/draft/render` to surface gaps, glossary matches, and bridge suggestions.
- Read flow: received messages show alignment references (idea POV, implicit references, related discussions, similarity to usual stance).
- Circle context: shared glossary, vision deltas, and exposure ledger cues are visible alongside messages.

## Source Tree (src)
```text
config/
  models.json          # Runtime model catalog + budget (hot reloaded)
src/
  sap_api/
    app.py              # FastAPI app entrypoint + router registration
    deps.py             # DB dependency wiring
    routes/
      health.py         # /v1/health
      workspace.py      # /v1/workspace/create, /v1/workspace/{id}
      actor.py          # /v1/actor/create, /v1/actor/{id}
      ingest.py         # /v1/artifact/ingest
      capsule.py        # /v1/capsule/query
      draft.py          # /v1/draft/analyze, /v1/draft/render
      skills.py         # /v1/skills/report, /v1/skills/earn, /v1/skills/query
  sap_core/
    domain/models.py    # Enums + Pydantic domain/request/response models
    retrieval/retrieve.py
    scoring/scoring.py
    prompts/templates.py
    privacy/partitioning.py
    pipelines/
      ingest.py         # Artifact ingest + chunking
      draft_analyze.py  # Fast-pass gap/mismatch analysis
      draft_render.py   # Render pipeline (LLM optional)
      skills.py         # Skill claim/evidence storage + privacy filtering
  sap_models/
    catalog.py          # Local model catalog + budget-aware selection
    config.py           # Runtime model config loader (hot reload via mtime)
    registry.py         # LLM instance cache
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
        0004_skills.sql
  sap_workers/
    worker.py           # Minimal job runner stub
```

## Key Concepts (alignment to docs)
- Capsules are the only publishable boundary objects; raw artifacts stay local.
- Retrieval uses guardrail capsules (goals/constraints/decisions) plus FTS/embeddings.
- Draft analysis is deterministic (no-LLM) in the fast pass; LLM rendering is optional and gated.
- Skills use explicit scopes; institution views exclude private scope and redact evidence by default.
- Model routing is budget-aware: pick local models by tier/latency/memory before using larger options.
