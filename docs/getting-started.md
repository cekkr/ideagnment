# Getting Started

This walkthrough exercises the minimal end-to-end flow: create a workspace, create an actor, ingest an artifact, and analyze a draft.

## 0) Run the API
```bash
pip install -e .
uvicorn sap_api.app:app --host 127.0.0.1 --port 8787
```

## 1) Create a workspace
```bash
curl -s -X POST http://127.0.0.1:8787/v1/workspace/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Workspace",
    "description": "Local test workspace"
  }'
```

Example response:
```json
{
  "workspace_id": "01HTW5S1Z2Z2M4Q9GZKQ9ZK1F3",
  "name": "Demo Workspace",
  "description": "Local test workspace",
  "created_at": "2024-02-06T12:00:00.000000",
  "owner_org_id": null,
  "default_scope": "workspace_local",
  "enabled_lenses": ["manufacturing", "academic", "management", "policy_outsider"]
}
```

## 2) Create an actor
```bash
curl -s -X POST http://127.0.0.1:8787/v1/actor/create \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "01HTW5S1Z2Z2M4Q9GZKQ9ZK1F3",
    "display_name": "Alex Rivera",
    "org_id": "org_demo"
  }'
```

Example response:
```json
{
  "actor_id": "01HTW5S3C4D2N1K5K7M4VY6C2A",
  "workspace_id": "01HTW5S1Z2Z2M4Q9GZKQ9ZK1F3",
  "display_name": "Alex Rivera",
  "org_id": "org_demo",
  "roles": []
}
```

## 3) Ingest an artifact
```bash
curl -s -X POST http://127.0.0.1:8787/v1/artifact/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "01HTW5S1Z2Z2M4Q9GZKQ9ZK1F3",
    "type": "doc",
    "title": "Project goals",
    "body": "Goal: reduce onboarding time to under 2 days."
  }'
```

Example response:
```json
{
  "artifact_id": "01HTW5S6Q8TQ0M7K7N5A9C2H2B",
  "chunks_created": 1,
  "embeddings_created": 0
}
```

## 4) Analyze a draft
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

Example response (shape only; values vary by data):
```json
{
  "mode": "before_send",
  "workspace_id": "01HTW5S1Z2Z2M4Q9GZKQ9ZK1F3",
  "recipients": ["01HTW5S3C4D2N1K5K7M4VY6C2A"],
  "lens_target": null,
  "blockers": [],
  "clarity_gaps": [
    {
      "span": [0, 33],
      "kind": "glossary_missing",
      "description": "Term may be unfamiliar to recipient.",
      "recipient_actor_id": "01HTW5S3C4D2N1K5K7M4VY6C2A",
      "suggested_bridge": null,
      "supporting_capsule_ids": [],
      "confidence": 0.62
    }
  ],
  "rare_thoughts": [],
  "context_capsule_ids": [],
  "policy_decision": "sidebar"
}
```

If you want a fuller walkthrough that includes capsules, lens rendering, or skills, add a few glossary/constraint capsules and re-run `/v1/draft/analyze`.
