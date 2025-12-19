# ideagnment

SAP (Semantic Alignment Protocol) is a local-first alignment service that ingests artifacts, builds structured capsules, and analyzes drafts for semantic gaps and expectation mismatches. The codebase follows the roadmap in `docs/` and is scaffolded under `src/`.

Privacy and data possession are central: sensitive skill claims/evidence default to private scope, and institution-facing views must not reveal private evidence. Decentralized instances keep their own data, sharing only what is explicitly published.

- Roadmap/specs: `docs/semanticAlignmentProtocol-roadmap.md`, `docs/skeleton.md`
- Project structure + status: `AI_REFERENCE.md`

## Quickstart (dev)
1. Install dependencies: `pip install -e .`
2. Run the API: `uvicorn sap_api.app:app --host 127.0.0.1 --port 8787`

## Repo Structure (high level)
- `src/sap_api/`: FastAPI app + routes
- `src/sap_core/`: domain models, retrieval, scoring, pipelines
- `src/sap_store/`: SQLite storage + migrations
- `src/sap_models/`: optional local model wrappers
- `src/sap_workers/`: background job runner stub
