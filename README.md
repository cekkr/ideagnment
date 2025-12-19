# ideagnment

SAP (Semantic Alignment Protocol) is a local-first alignment layer that sits behind communication tools and helps teams keep shared context aligned. It ingests artifacts, builds structured capsules (goals, constraints, decisions, glossary, positions), and analyzes drafts *before send* for semantic gaps and expectation mismatches, while preserving dissent and author voice.

This repo is a Python service scaffold that follows the project roadmap in `docs/` and the current structure/status in `AI_REFERENCE.md`.

- Roadmap/specs: `docs/semanticAlignmentProtocol-roadmap.md`, `docs/skeleton.md`
- Origin concept prompt: `docs/main-prompt-concept.md`
- Getting started workflow: `docs/getting-started.md`
- Milestone A checklist: `docs/milestone-a-checklist.md`
- Project structure + status: `AI_REFERENCE.md`
- Mock messaging demo: `examples/mock_messaging/index.html` (served by `examples/mock_messaging/server.py`)

## Why this exists
Complex projects fail at the seams: unstated assumptions, silent contradictions, and outsider ideas that never land. SAP is not "rewrite-to-conform." It is sensemaking + mismatch detection + bridge-building with provenance and opt-in control. It should help people align their visions without creating dependency; if the service is lacking, people should still be able to discuss and share perspectives. The goal is "human learning" support for difficult conversations, not a constraining tool.

## Core principles
- Local-first by default: drafts and raw artifacts stay on-device.
- Capsules are the only publishable boundary objects.
- No silent rewriting: suggestions only, author stays in control.
- Dissent preservation: rare thoughts are framed, not normalized.
- Provenance is mandatory for any warning or suggestion.

## What’s here now
The codebase is an early scaffold with a real API surface and storage:
- FastAPI endpoints for ingestion, capsule query, draft analyze/render, and skills.
- SQLite schema + migrations with FTS support and a simple job queue.
- Retrieval, scoring, and pipeline stubs for ingestion and draft analysis.
- Optional local model routing + catalog in `config/models.json`.
- Skills privacy partitioning with institution-safe views.
- Mock messaging web demo for circle-based alignment workflows in `examples/mock_messaging/index.html`.

## Roadmap (high level)
From `docs/semanticAlignmentProtocol-roadmap.md`:
- Milestone A: Local memory + retrieval (SQLite schema, FTS, embeddings, ingest pipeline).
- Milestone B: Gap + mismatch analysis (glossary/exposure ledger, fast-pass draft analysis).
- Milestone C: Multi-lens rendering (LLM router + render pipeline, optional LLM).
- Milestone D: After-receive explain + profiles (sender lens card, assumption signatures).
- Milestone E: Debate engine (idea clusters, contradictions, discriminating tests).
- Milestone F: Publish + federation (redaction, signing, CRDT/manifest sync).

## Architecture at a glance
SAP runs as a local daemon or a single service:
- Ingestion: chunking + embedding + capsule extraction (proposed then published).
- Context store: SQLite + FTS + optional vector index.
- Alignment engine: gap/mismatch detection + policy gating.
- Rendering engine: optional local LLM for lens-specific rewrites.
- Federation (optional): publishable capsules + signed sync.

## Key concepts
- **Capsules**: structured, addressable context units (Goal, Constraint, Decision, Glossary, Position, OpenQuestion).
- **Exposure ledger**: tracks what a recipient has actually seen.
- **Alignment report**: blockers, clarity gaps, context links, rare thought highlights.
- **Lenses**: discipline-aware renderings for cross‑domain clarity.

## Quickstart (dev)
1. Install dependencies: `pip install -e .`
2. Run the API: `uvicorn sap_api.app:app --host 127.0.0.1 --port 8787`

## API overview (v1)
Common endpoints:
- `GET /v1/health`
- `POST /v1/workspace/create`
- `POST /v1/actor/create`
- `POST /v1/artifact/ingest`
- `GET /v1/capsule/query`
- `POST /v1/draft/analyze`
- `POST /v1/draft/render`
- `POST /v1/skills/report`, `POST /v1/skills/earn`, `GET /v1/skills/query`

Example: create a workspace
```bash
curl -s -X POST http://127.0.0.1:8787/v1/workspace/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Workspace",
    "description": "Local test workspace"
  }'
```

Example: analyze a draft
```bash
curl -s -X POST http://127.0.0.1:8787/v1/draft/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "01HTW5S1Z2Z2M4Q9GZKQ9ZK1F3",
    "draft_text": "We will cut onboarding time with a new automation layer.",
    "recipients": ["01HTW5S3C4D2N1K5K7M4VY6C2A"],
    "mode": "before_send"
  }'
```

See `docs/getting-started.md` for a full end-to-end walkthrough with responses.

## Runtime configuration
- Model catalog: edit `config/models.json` (hot reload on file change). Override path with `SAP_MODEL_CATALOG_PATH`.
- Skills endpoints: pass `X-Actor-Id` header (and `X-Org-Id` for institution views).

## Repo structure (high level)
- `src/sap_api/`: FastAPI app + routes
- `src/sap_core/`: domain models, retrieval, scoring, pipelines
- `src/sap_store/`: SQLite storage + migrations
- `src/sap_models/`: local model catalog/router + optional LLM wrappers
- `src/sap_workers/`: background job runner stub

## Contributing
This is an early-stage scaffold. If you want to help, start by aligning changes with the roadmap and keeping `AI_REFERENCE.md` and `README.md` in sync.

## License
See `LICENSE`.
