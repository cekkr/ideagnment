Below are **all 4 artifacts** in one place:

1. **OpenAPI 3.1 spec (YAML)**
2. **SQLite migrations (SQL files)**
3. **Repo skeleton with concrete code blocks (FastAPI + pipelines + worker + model router stubs)**
4. **Exact prompt templates + deterministic scoring functions (ready-to-paste Python)**

---

# 1) OpenAPI 3.1 spec (v1)

Save as: `openapi.yaml`

```yaml
openapi: 3.1.0
info:
  title: SAP Service API
  version: "0.2"
servers:
  - url: http://127.0.0.1:8787
paths:
  /v1/health:
    get:
      summary: Health check
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/HealthResponse"

  /v1/workspace/create:
    post:
      summary: Create workspace
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/WorkspaceCreateRequest"
      responses:
        "200":
          description: Workspace created
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Workspace"

  /v1/workspace/{workspace_id}:
    get:
      summary: Get workspace
      parameters:
        - in: path
          name: workspace_id
          required: true
          schema: { type: string }
      responses:
        "200":
          description: Workspace
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Workspace"

  /v1/workspace/{workspace_id}/policy:
    put:
      summary: Upsert workspace policy
      parameters:
        - in: path
          name: workspace_id
          required: true
          schema: { type: string }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/PolicyConfig"
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/PolicyConfig"

  /v1/artifact/ingest:
    post:
      summary: Ingest artifact (message/doc/etc.)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ArtifactIngestRequest"
      responses:
        "200":
          description: Ingest result
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ArtifactIngestResponse"

  /v1/capsule/propose:
    post:
      summary: Propose capsule (manual or AI-assisted)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CapsuleProposeRequest"
      responses:
        "200":
          description: Proposed capsule
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Capsule"

  /v1/capsule/publish:
    post:
      summary: Publish capsule (optional redaction + signing)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CapsulePublishRequest"
      responses:
        "200":
          description: Published capsule
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Capsule"

  /v1/capsule/query:
    get:
      summary: Query capsules
      parameters:
        - in: query
          name: workspace_id
          required: true
          schema: { type: string }
        - in: query
          name: type
          required: false
          schema: { $ref: "#/components/schemas/CapsuleType" }
        - in: query
          name: lens
          required: false
          schema: { $ref: "#/components/schemas/Lens" }
        - in: query
          name: scope
          required: false
          schema: { $ref: "#/components/schemas/Scope" }
        - in: query
          name: q
          required: false
          schema: { type: string }
        - in: query
          name: limit
          required: false
          schema: { type: integer, default: 50 }
      responses:
        "200":
          description: Capsule list
          content:
            application/json:
              schema:
                type: array
                items: { $ref: "#/components/schemas/Capsule" }

  /v1/draft/analyze:
    post:
      summary: Analyze a draft for gaps/mismatches/rare-thoughts
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DraftAnalyzeRequest"
      responses:
        "200":
          description: Alignment report
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/AlignmentReport"

  /v1/draft/render:
    post:
      summary: Render a draft for a target lens (minimal bridge / outsider)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/DraftRenderRequest"
      responses:
        "200":
          description: Render result
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/DraftRenderResponse"

  /v1/message/explain:
    post:
      summary: Explain an incoming message (sender lens card, assumptions, questions)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/MessageExplainRequest"
      responses:
        "200":
          description: Explanation report
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/MessageExplainResponse"

  /v1/ideas/map:
    post:
      summary: Build an idea map (clusters, stance axes, contradiction seeds)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/IdeaMapRequest"
      responses:
        "200":
          description: Idea map
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/IdeaMapResponse"

  /v1/ideas/summarize_by_lens:
    post:
      summary: Summarize a topic/corpus by lens
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/IdeaSummarizeByLensRequest"
      responses:
        "200":
          description: Summaries
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/IdeaSummarizeByLensResponse"

  /v1/exposure/log:
    post:
      summary: Log that an actor has seen/acked a capsule
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ExposureEvent"
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ExposureEvent"

  /v1/trust/add_key:
    post:
      summary: Add a trusted public key for federation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/TrustKey"
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/TrustKey"

  /v1/sync/pull:
    post:
      summary: Pull capsules from a peer (request format)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/SyncPullRequest"
      responses:
        "200":
          description: Sync pull response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/SyncPullResponse"

  /v1/sync/push:
    post:
      summary: Push capsules to a peer (request format)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/SyncPushRequest"
      responses:
        "200":
          description: Sync push response
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/SyncPushResponse"

components:
  schemas:
    HealthResponse:
      type: object
      properties:
        status: { type: string }
        version: { type: string }
        models_loaded:
          type: object
          additionalProperties: { type: boolean }
      required: [status, version, models_loaded]

    Lens:
      type: string
      enum: [manufacturing, academic, management, policy_outsider]

    CapsuleType:
      type: string
      enum: [goal, constraint, decision, glossary, capability, assumption, evidence, position, open_question]

    Scope:
      type: string
      enum: [private, workspace_local, org_local, consortium_shared]

    EvidenceLevel:
      type: string
      enum: [hypothesis, estimate, simulated, measured, certified]

    ArtifactType:
      type: string
      enum: [email, chat, doc, issue, pr, meeting_notes, transcript, misc]

    AnalysisMode:
      type: string
      enum: [typing, before_send, after_receive, batch]

    Workspace:
      type: object
      properties:
        workspace_id: { type: string }
        name: { type: string }
        description: { type: string }
        created_at: { type: string, format: date-time }
        owner_org_id: { type: [string, "null"] }
        default_scope: { $ref: "#/components/schemas/Scope" }
        enabled_lenses:
          type: array
          items: { $ref: "#/components/schemas/Lens" }
      required: [workspace_id, name, created_at, default_scope, enabled_lenses]

    WorkspaceCreateRequest:
      type: object
      properties:
        name: { type: string }
        description: { type: string }
        owner_org_id: { type: [string, "null"] }
        default_scope: { $ref: "#/components/schemas/Scope" }
      required: [name]

    PolicyConfig:
      type: object
      properties:
        workspace_id: { type: string }
        blocker_conf_modal: { type: number, default: 0.88 }
        blocker_conf_badge: { type: number, default: 0.80 }
        hint_value_sidebar: { type: number, default: 0.65 }
        allow_llm_on_typing: { type: boolean, default: false }
        allow_llm_before_send: { type: boolean, default: true }
        allow_external_sync: { type: boolean, default: false }
        expected_evidence_by_lens:
          type: object
          additionalProperties:
            $ref: "#/components/schemas/EvidenceLevel"
      required: [workspace_id]

    Provenance:
      type: object
      properties:
        source_artifact_ids:
          type: array
          items: { type: string }
        source_spans:
          type: array
          items:
            type: object
            properties:
              artifact_id: { type: string }
              chunk_id: { type: [string, "null"] }
              start_char: { type: integer }
              end_char: { type: integer }
            required: [artifact_id, start_char, end_char]
        notes: { type: [string, "null"] }

    Capsule:
      type: object
      properties:
        capsule_id: { type: string }
        workspace_id: { type: string }
        type: { $ref: "#/components/schemas/CapsuleType" }
        lens_tags:
          type: array
          items: { $ref: "#/components/schemas/Lens" }
        scope: { $ref: "#/components/schemas/Scope" }
        title: { type: string }
        body: { type: string }
        evidence_level: { $ref: "#/components/schemas/EvidenceLevel" }
        confidence: { type: number, minimum: 0.0, maximum: 1.0 }
        created_at: { type: string, format: date-time }
        created_by_actor_id: { type: [string, "null"] }
        provenance: { $ref: "#/components/schemas/Provenance" }
        is_published: { type: boolean }
        redaction_profile_id: { type: [string, "null"] }
        content_hash: { type: [string, "null"] }
        signer_key_id: { type: [string, "null"] }
        signature_b64: { type: [string, "null"] }
        meta:
          type: object
          additionalProperties: true
      required: [capsule_id, workspace_id, type, title, body, scope, evidence_level, confidence, created_at, is_published, meta]

    ArtifactIngestRequest:
      type: object
      properties:
        workspace_id: { type: string }
        type: { $ref: "#/components/schemas/ArtifactType" }
        title: { type: [string, "null"] }
        body: { type: string }
        created_by_actor_id: { type: [string, "null"] }
        meta:
          type: object
          additionalProperties: true
      required: [workspace_id, type, body]

    ArtifactIngestResponse:
      type: object
      properties:
        artifact_id: { type: string }
        chunks_created: { type: integer }
        embeddings_created: { type: integer }
        jobs_queued:
          type: array
          items: { type: string }
      required: [artifact_id, chunks_created, embeddings_created, jobs_queued]

    CapsuleProposeRequest:
      type: object
      properties:
        workspace_id: { type: string }
        type: { $ref: "#/components/schemas/CapsuleType" }
        title: { type: string }
        body: { type: string }
        lens_tags:
          type: array
          items: { $ref: "#/components/schemas/Lens" }
        scope: { $ref: "#/components/schemas/Scope" }
        evidence_level: { $ref: "#/components/schemas/EvidenceLevel" }
        confidence: { type: number }
        provenance: { $ref: "#/components/schemas/Provenance" }
        meta:
          type: object
          additionalProperties: true
      required: [workspace_id, type, title, body]

    CapsulePublishRequest:
      type: object
      properties:
        capsule_id: { type: string }
        publish_scope: { $ref: "#/components/schemas/Scope" }
        redaction_profile_id: { type: [string, "null"] }
        signer_key_id: { type: [string, "null"] }
      required: [capsule_id, publish_scope]

    DraftAnalyzeRequest:
      type: object
      properties:
        workspace_id: { type: string }
        draft_text: { type: string }
        sender_actor_id: { type: [string, "null"] }
        recipients:
          type: array
          items: { type: string }
        recipient_lenses:
          type: array
          items: { $ref: "#/components/schemas/Lens" }
        mode: { $ref: "#/components/schemas/AnalysisMode" }
        draft_id: { type: [string, "null"] }
        changed_spans:
          type: array
          items:
            type: array
            minItems: 2
            maxItems: 2
            items: { type: integer }
        max_findings: { type: integer, default: 30 }
      required: [workspace_id, draft_text]

    GapFinding:
      type: object
      properties:
        span:
          type: array
          minItems: 2
          maxItems: 2
          items: { type: integer }
        kind: { type: string }
        description: { type: string }
        recipient_actor_id: { type: [string, "null"] }
        suggested_bridge: { type: [string, "null"] }
        supporting_capsule_ids:
          type: array
          items: { type: string }
        confidence: { type: number, minimum: 0.0, maximum: 1.0 }
      required: [span, kind, description, confidence]

    MismatchFinding:
      type: object
      properties:
        span:
          type: array
          minItems: 2
          maxItems: 2
          items: { type: integer }
        kind: { type: string }
        description: { type: string }
        conflicting_capsule_id: { type: [string, "null"] }
        recommendation: { type: [string, "null"] }
        confidence: { type: number, minimum: 0.0, maximum: 1.0 }
      required: [span, kind, description, confidence]

    RareThoughtFinding:
      type: object
      properties:
        span:
          type: array
          minItems: 2
          maxItems: 2
          items: { type: integer }
        idea_summary: { type: string }
        fit_map:
          type: array
          items: { type: string }
        protect_notes: { type: string }
        novelty: { type: number, minimum: 0.0, maximum: 1.0 }
        relevance: { type: number, minimum: 0.0, maximum: 1.0 }
      required: [span, idea_summary, protect_notes, novelty, relevance]

    AlignmentReport:
      type: object
      properties:
        mode: { $ref: "#/components/schemas/AnalysisMode" }
        workspace_id: { type: string }
        recipients:
          type: array
          items: { type: string }
        lens_target: { $ref: "#/components/schemas/Lens" }
        blockers:
          type: array
          items: { $ref: "#/components/schemas/MismatchFinding" }
        clarity_gaps:
          type: array
          items: { $ref: "#/components/schemas/GapFinding" }
        rare_thoughts:
          type: array
          items: { $ref: "#/components/schemas/RareThoughtFinding" }
        context_capsule_ids:
          type: array
          items: { type: string }
        policy_decision: { type: string }
      required: [mode, workspace_id, blockers, clarity_gaps, rare_thoughts, context_capsule_ids, policy_decision]

    DraftRenderRequest:
      type: object
      properties:
        workspace_id: { type: string }
        draft_text: { type: string }
        recipients:
          type: array
          items: { type: string }
        target_lens: { $ref: "#/components/schemas/Lens" }
        style: { type: string, default: "minimal_bridge" }
        max_added_chars: { type: integer, default: 500 }
      required: [workspace_id, draft_text, target_lens]

    DraftRenderResponse:
      type: object
      properties:
        native: { type: string }
        rendered: { type: string }
        diff_summary:
          type: array
          items: { type: string }
        inserted_glossary:
          type: array
          items: { type: string }
        used_capsule_ids:
          type: array
          items: { type: string }
      required: [native, rendered, used_capsule_ids]

    MessageExplainRequest:
      type: object
      properties:
        workspace_id: { type: string }
        message_text: { type: string }
        sender_hint: { type: [string, "null"] }
        assumed_sender_actor_id: { type: [string, "null"] }
        recipient_actor_id: { type: [string, "null"] }
        target_lens: { $ref: "#/components/schemas/Lens" }
      required: [workspace_id, message_text]

    SenderLensCard:
      type: object
      properties:
        inferred_lens: { $ref: "#/components/schemas/Lens" }
        evidence_style: { type: string }
        likely_constraints_optimized:
          type: array
          items: { type: string }
        assumed_prereqs:
          type: array
          items: { type: string }
        recommended_questions:
          type: array
          items: { type: string }
      required: [inferred_lens, evidence_style, likely_constraints_optimized, assumed_prereqs, recommended_questions]

    MessageExplainResponse:
      type: object
      properties:
        report: { $ref: "#/components/schemas/AlignmentReport" }
        sender_card: { $ref: "#/components/schemas/SenderLensCard" }
      required: [report, sender_card]

    IdeaMapRequest:
      type: object
      properties:
        workspace_id: { type: string }
        query: { type: [string, "null"] }
        lens: { $ref: "#/components/schemas/Lens" }
        limit_chunks: { type: integer, default: 400 }
        include_positions: { type: boolean, default: true }
      required: [workspace_id]

    IdeaCluster:
      type: object
      properties:
        cluster_id: { type: string }
        label: { type: string }
        capsule_ids:
          type: array
          items: { type: string }
        chunk_ids:
          type: array
          items: { type: string }
        centroid_terms:
          type: array
          items: { type: string }
      required: [cluster_id, label, capsule_ids, chunk_ids]

    StanceAxis:
      type: object
      properties:
        axis_id: { type: string }
        topic: { type: string }
        pole_a_label: { type: string }
        pole_b_label: { type: string }
        supporting_position_capsules_a:
          type: array
          items: { type: string }
        supporting_position_capsules_b:
          type: array
          items: { type: string }
      required: [axis_id, topic, pole_a_label, pole_b_label]

    ContradictionSeed:
      type: object
      properties:
        seed_id: { type: string }
        claim_a: { type: string }
        claim_b: { type: string }
        evidence_capsule_ids:
          type: array
          items: { type: string }
        discriminating_tests:
          type: array
          items: { type: string }
      required: [seed_id, claim_a, claim_b]

    IdeaMapResponse:
      type: object
      properties:
        workspace_id: { type: string }
        query: { type: [string, "null"] }
        clusters:
          type: array
          items: { $ref: "#/components/schemas/IdeaCluster" }
        stance_axes:
          type: array
          items: { $ref: "#/components/schemas/StanceAxis" }
        contradiction_seeds:
          type: array
          items: { $ref: "#/components/schemas/ContradictionSeed" }
        outlier_seeds:
          type: array
          items: { type: string }
      required: [workspace_id, clusters, stance_axes, contradiction_seeds, outlier_seeds]

    IdeaSummarizeByLensRequest:
      type: object
      properties:
        workspace_id: { type: string }
        query: { type: [string, "null"] }
        max_chunks: { type: integer, default: 300 }
      required: [workspace_id]

    IdeaSummarizeByLensResponse:
      type: object
      properties:
        manufacturing: { type: string }
        academic: { type: string }
        management: { type: string }
        policy_outsider: { type: string }
      required: [manufacturing, academic, management, policy_outsider]

    ExposureEvent:
      type: object
      properties:
        workspace_id: { type: string }
        actor_id: { type: string }
        capsule_id: { type: string }
        exposure_type: { type: string, default: "seen" }
        timestamp: { type: string, format: date-time }
        strength: { type: number, minimum: 0.0, maximum: 1.0, default: 0.7 }
      required: [workspace_id, actor_id, capsule_id, exposure_type, timestamp, strength]

    TrustKey:
      type: object
      properties:
        key_id: { type: string }
        org_id: { type: [string, "null"] }
        label: { type: [string, "null"] }
        ed25519_pub_b64: { type: string }
        trust_level: { type: string, enum: [local, org, consortium] }
        added_at: { type: string, format: date-time }
      required: [key_id, ed25519_pub_b64, trust_level, added_at]

    SyncPullRequest:
      type: object
      properties:
        workspace_id: { type: string }
        known_capsule_ids:
          type: array
          items: { type: string }
        want_since: { type: [string, "null"], format: date-time }
      required: [workspace_id, known_capsule_ids]

    SyncPullResponse:
      type: object
      properties:
        workspace_id: { type: string }
        capsules:
          type: array
          items: { $ref: "#/components/schemas/Capsule" }
        edges:
          type: array
          items: { type: object, additionalProperties: true }
      required: [workspace_id, capsules, edges]

    SyncPushRequest:
      type: object
      properties:
        workspace_id: { type: string }
        from_org_id: { type: string }
        capsules:
          type: array
          items: { $ref: "#/components/schemas/Capsule" }
        edges:
          type: array
          items: { type: object, additionalProperties: true }
      required: [workspace_id, from_org_id, capsules]

    SyncPushResponse:
      type: object
      properties:
        workspace_id: { type: string }
        accepted_capsules: { type: integer }
        rejected_capsules: { type: integer }
        errors:
          type: array
          items: { type: string }
      required: [workspace_id, accepted_capsules, rejected_capsules, errors]
```

---

# 2) SQLite migrations (ready to use)

Create folder `sap_store/sqlite/migrations/` and add:

## `0001_init.sql`

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspace (
  workspace_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL,
  owner_org_id TEXT,
  default_scope TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actor (
  actor_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  org_id TEXT,
  roles_json TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS artifact (
  artifact_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL,
  created_by_actor_id TEXT,
  meta_json TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS chunk (
  chunk_id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL,
  workspace_id TEXT NOT NULL,
  start_char INTEGER NOT NULL,
  end_char INTEGER NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (artifact_id) REFERENCES artifact(artifact_id),
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

-- Embeddings stored as JSON array to keep MVP dependency-free.
-- Swap later to sqlite-vec or BLOB float32.
CREATE TABLE IF NOT EXISTS embedding (
  embedding_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  owner_type TEXT NOT NULL,     -- "chunk" | "capsule" | "profile"
  owner_id TEXT NOT NULL,
  dim INTEGER NOT NULL,
  vec_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS capsule (
  capsule_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  lens_tags_json TEXT,
  scope TEXT NOT NULL,
  evidence_level TEXT NOT NULL,
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL,
  created_by_actor_id TEXT,
  provenance_json TEXT,
  is_published INTEGER NOT NULL DEFAULT 0,
  redaction_profile_id TEXT,
  content_hash TEXT,
  signer_key_id TEXT,
  signature_b64 TEXT,
  meta_json TEXT,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS edge (
  edge_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  src_id TEXT NOT NULL,
  dst_id TEXT NOT NULL,
  rel TEXT NOT NULL,
  weight REAL NOT NULL DEFAULT 0.5,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS profile (
  profile_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  owner_actor_id TEXT,
  lens_primary TEXT,
  assumption_signature_json TEXT,
  glossary_exposure_json TEXT,
  stance_refs_json TEXT,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS exposure (
  exposure_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  capsule_id TEXT NOT NULL,
  exposure_type TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  strength REAL NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS policy (
  workspace_id TEXT PRIMARY KEY,
  policy_json TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS redaction_profile (
  redaction_profile_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  name TEXT NOT NULL,
  rules_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspace(workspace_id)
);

CREATE TABLE IF NOT EXISTS trust_key (
  key_id TEXT PRIMARY KEY,
  org_id TEXT,
  label TEXT,
  ed25519_pub_b64 TEXT NOT NULL,
  trust_level TEXT NOT NULL,
  added_at TEXT NOT NULL
);
```

## `0002_fts.sql`

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks
USING fts5(text, chunk_id UNINDEXED, workspace_id UNINDEXED);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_capsules
USING fts5(title, body, capsule_id UNINDEXED, workspace_id UNINDEXED);
```

## `0003_jobs.sql`

```sql
CREATE TABLE IF NOT EXISTS job (
  job_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL,          -- queued|running|done|failed
  priority INTEGER NOT NULL DEFAULT 5,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  error TEXT
);
```

---

# 3) Repo skeleton + concrete code blocks

## 3.1 `pyproject.toml`

```toml
[project]
name = "sap"
version = "0.2.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "uvicorn>=0.27",
  "pydantic>=2.6",
  "python-ulid>=2.7.0",
  "numpy>=1.26",
  "scikit-learn>=1.4",
  "regex>=2024.0.0"
]

[project.optional-dependencies]
models = [
  "sentence-transformers>=3.0.0",
  "llama-cpp-python>=0.2.90"
]
dev = [
  "pytest>=8.0",
  "ruff>=0.5.0"
]

[tool.ruff]
line-length = 100
```

## 3.2 File tree

```text
sap/
  pyproject.toml
  openapi.yaml
  sap_api/
    app.py
    deps.py
    routes/
      health.py
      workspace.py
      ingest.py
      capsule.py
      draft.py
      message.py
      ideas.py
      exposure.py
      trust.py
      sync.py
  sap_core/
    domain/models.py
    retrieval/retrieve.py
    scoring/scoring.py
    prompts/templates.py
    pipelines/ingest.py
    pipelines/draft_analyze.py
    pipelines/draft_render.py
    pipelines/message_explain.py
    pipelines/ideas_map.py
    pipelines/ideas_summarize.py
  sap_models/
    router.py
    embedder.py
    llm.py
  sap_store/
    sqlite/db.py
    sqlite/migrate.py
    sqlite/migrations/0001_init.sql
    sqlite/migrations/0002_fts.sql
    sqlite/migrations/0003_jobs.sql
  sap_workers/
    worker.py
    jobs.py
```

---

## 3.3 Domain models: `sap_core/domain/models.py`

```python
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class Lens(str, Enum):
    manufacturing = "manufacturing"
    academic = "academic"
    management = "management"
    policy_outsider = "policy_outsider"


class CapsuleType(str, Enum):
    goal = "goal"
    constraint = "constraint"
    decision = "decision"
    glossary = "glossary"
    capability = "capability"
    assumption = "assumption"
    evidence = "evidence"
    position = "position"
    open_question = "open_question"


class Scope(str, Enum):
    private = "private"
    workspace_local = "workspace_local"
    org_local = "org_local"
    consortium_shared = "consortium_shared"


class EvidenceLevel(str, Enum):
    hypothesis = "hypothesis"
    estimate = "estimate"
    simulated = "simulated"
    measured = "measured"
    certified = "certified"


class ArtifactType(str, Enum):
    email = "email"
    chat = "chat"
    doc = "doc"
    issue = "issue"
    pr = "pr"
    meeting_notes = "meeting_notes"
    transcript = "transcript"
    misc = "misc"


class AnalysisMode(str, Enum):
    typing = "typing"
    before_send = "before_send"
    after_receive = "after_receive"
    batch = "batch"


class SourceSpan(BaseModel):
    artifact_id: str
    chunk_id: Optional[str] = None
    start_char: int
    end_char: int


class Provenance(BaseModel):
    source_artifact_ids: List[str] = Field(default_factory=list)
    source_spans: List[SourceSpan] = Field(default_factory=list)
    notes: Optional[str] = None


class Workspace(BaseModel):
    workspace_id: str
    name: str
    description: str = ""
    created_at: datetime
    owner_org_id: Optional[str] = None
    default_scope: Scope = Scope.workspace_local
    enabled_lenses: List[Lens] = Field(default_factory=lambda: list(Lens))


class PolicyConfig(BaseModel):
    workspace_id: str
    blocker_conf_modal: float = 0.88
    blocker_conf_badge: float = 0.80
    hint_value_sidebar: float = 0.65
    allow_llm_on_typing: bool = False
    allow_llm_before_send: bool = True
    allow_external_sync: bool = False
    expected_evidence_by_lens: Dict[Lens, EvidenceLevel] = Field(
        default_factory=lambda: {
            Lens.manufacturing: EvidenceLevel.measured,
            Lens.academic: EvidenceLevel.simulated,
            Lens.management: EvidenceLevel.estimate,
            Lens.policy_outsider: EvidenceLevel.estimate,
        }
    )


class Capsule(BaseModel):
    capsule_id: str
    workspace_id: str
    type: CapsuleType
    lens_tags: List[Lens] = Field(default_factory=list)
    scope: Scope = Scope.workspace_local
    title: str
    body: str
    evidence_level: EvidenceLevel = EvidenceLevel.hypothesis
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    created_at: datetime
    created_by_actor_id: Optional[str] = None
    provenance: Provenance = Field(default_factory=Provenance)
    is_published: bool = False
    redaction_profile_id: Optional[str] = None
    content_hash: Optional[str] = None
    signer_key_id: Optional[str] = None
    signature_b64: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class ExposureEvent(BaseModel):
    workspace_id: str
    actor_id: str
    capsule_id: str
    exposure_type: str = "seen"
    timestamp: datetime
    strength: float = Field(default=0.7, ge=0.0, le=1.0)


class GapFinding(BaseModel):
    span: Tuple[int, int]
    kind: str
    description: str
    recipient_actor_id: Optional[str] = None
    suggested_bridge: Optional[str] = None
    supporting_capsule_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class MismatchFinding(BaseModel):
    span: Tuple[int, int]
    kind: str
    description: str
    conflicting_capsule_id: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class RareThoughtFinding(BaseModel):
    span: Tuple[int, int]
    idea_summary: str
    fit_map: List[str] = Field(default_factory=list)
    protect_notes: str
    novelty: float = Field(ge=0.0, le=1.0)
    relevance: float = Field(ge=0.0, le=1.0)


class AlignmentReport(BaseModel):
    mode: AnalysisMode
    workspace_id: str
    recipients: List[str] = Field(default_factory=list)
    lens_target: Optional[Lens] = None
    blockers: List[MismatchFinding] = Field(default_factory=list)
    clarity_gaps: List[GapFinding] = Field(default_factory=list)
    rare_thoughts: List[RareThoughtFinding] = Field(default_factory=list)
    context_capsule_ids: List[str] = Field(default_factory=list)
    policy_decision: str = "silent"
```

---

## 3.4 SQLite access + migrations

### `sap_store/sqlite/db.py`

```python
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".sap" / "sap.db"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    ensure_parent(db_path)
    con = sqlite3.connect(str(db_path), check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON;")
    return con


@contextmanager
def db_session(db_path: Path = DEFAULT_DB_PATH):
    con = connect(db_path)
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()
```

### `sap_store/sqlite/migrate.py`

```python
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from .db import db_session, DEFAULT_DB_PATH

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def ensure_migrations_table(con):
    con.execute("""
      CREATE TABLE IF NOT EXISTS schema_migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL UNIQUE,
        applied_at TEXT NOT NULL
      );
    """)


def applied(con) -> set[str]:
    rows = con.execute("SELECT filename FROM schema_migrations").fetchall()
    return {r["filename"] for r in rows}


def apply_all(db_path: Path = DEFAULT_DB_PATH) -> None:
    with db_session(db_path) as con:
        ensure_migrations_table(con)
        done = applied(con)
        files = sorted(p for p in MIGRATIONS_DIR.glob("*.sql"))
        for f in files:
            if f.name in done:
                continue
            sql = f.read_text(encoding="utf-8")
            con.executescript(sql)
            con.execute(
                "INSERT INTO schema_migrations(filename, applied_at) VALUES(?, ?)",
                (f.name, datetime.utcnow().isoformat()),
            )
```

---

## 3.5 Model router + embedder + LLM stubs

### `sap_models/router.py`

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from sap_core.domain.models import AnalysisMode


@dataclass
class RouteDecision:
    allow_llm: bool
    llm_tier: str = "small"
    max_tokens: int = 280
    temperature: float = 0.2


class ModelRouter:
    def __init__(self, allow_llm_on_typing: bool, allow_llm_before_send: bool):
        self.allow_llm_on_typing = allow_llm_on_typing
        self.allow_llm_before_send = allow_llm_before_send

    def route(self, mode: AnalysisMode, value_score: float) -> RouteDecision:
        if mode == AnalysisMode.typing:
            return RouteDecision(allow_llm=self.allow_llm_on_typing and value_score > 0.85, llm_tier="small", max_tokens=160)
        if mode == AnalysisMode.before_send:
            return RouteDecision(allow_llm=self.allow_llm_before_send and value_score > 0.55, llm_tier="small", max_tokens=320)
        if mode == AnalysisMode.batch:
            return RouteDecision(allow_llm=True, llm_tier="medium", max_tokens=700, temperature=0.15)
        return RouteDecision(allow_llm=False)
```

### `sap_models/embedder.py` (works if optional deps installed)

```python
from __future__ import annotations
from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None


class LocalEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers not installed. Install with: pip install sap[models]")
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        vecs = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vecs.astype(np.float32).tolist()
```

### `sap_models/llm.py` (optional)

```python
from __future__ import annotations

try:
    from llama_cpp import Llama
except Exception:  # pragma: no cover
    Llama = None


class LocalLLM:
    def __init__(self, gguf_path: str, n_ctx: int = 4096):
        if Llama is None:
            raise RuntimeError("llama-cpp-python not installed. Install with: pip install sap[models]")
        self.llm = Llama(model_path=gguf_path, n_ctx=n_ctx, verbose=False)

    def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.2) -> str:
        out = self.llm(prompt, max_tokens=max_tokens, temperature=temperature, stop=["</OUTPUT>"])
        return out["choices"][0]["text"].strip()
```

---

## 3.6 Retrieval: `sap_core/retrieval/retrieve.py`

This MVP retrieval uses **FTS + naive cosine over stored JSON vectors** (good enough to ship v0.2; you can swap to sqlite-vec later).

```python
from __future__ import annotations
from typing import List, Optional, Tuple
import json
import numpy as np
from sap_core.domain.models import Capsule, CapsuleType, Lens, Scope


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    return float(np.dot(a, b) / denom)


def fts_capsules(con, workspace_id: str, q: str, limit: int = 30) -> List[str]:
    rows = con.execute(
        "SELECT capsule_id FROM fts_capsules WHERE fts_capsules MATCH ? AND workspace_id=? LIMIT ?",
        (q, workspace_id, limit),
    ).fetchall()
    return [r["capsule_id"] for r in rows]


def load_capsules(con, workspace_id: str, ids: List[str]) -> List[Capsule]:
    if not ids:
        return []
    qmarks = ",".join("?" for _ in ids)
    rows = con.execute(
        f"SELECT * FROM capsule WHERE workspace_id=? AND capsule_id IN ({qmarks})",
        [workspace_id, *ids],
    ).fetchall()

    out: List[Capsule] = []
    for r in rows:
        out.append(
            Capsule(
                capsule_id=r["capsule_id"],
                workspace_id=r["workspace_id"],
                type=CapsuleType(r["type"]),
                title=r["title"],
                body=r["body"],
                lens_tags=json.loads(r["lens_tags_json"] or "[]"),
                scope=Scope(r["scope"]),
                evidence_level=r["evidence_level"],
                confidence=float(r["confidence"]),
                created_at=np.datetime64(r["created_at"]).astype("datetime64[ms]").astype(object),
                created_by_actor_id=r["created_by_actor_id"],
                provenance=json.loads(r["provenance_json"] or "{}"),
                is_published=bool(r["is_published"]),
                redaction_profile_id=r["redaction_profile_id"],
                content_hash=r["content_hash"],
                signer_key_id=r["signer_key_id"],
                signature_b64=r["signature_b64"],
                meta=json.loads(r["meta_json"] or "{}"),
            )
        )
    return out


def vector_top_capsules(con, workspace_id: str, query_vec: List[float], limit: int = 50) -> List[Tuple[str, float]]:
    q = con.execute(
        "SELECT owner_id, vec_json FROM embedding WHERE workspace_id=? AND owner_type='capsule'",
        (workspace_id,),
    ).fetchall()
    if not q:
        return []
    qv = np.array(query_vec, dtype=np.float32)
    scored = []
    for r in q:
        v = np.array(json.loads(r["vec_json"]), dtype=np.float32)
        scored.append((r["owner_id"], _cos(qv, v)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def retrieve_bundle(con, workspace_id: str, query: str, query_vec: Optional[List[float]] = None, limit: int = 40) -> List[Capsule]:
    # Guardrail capsules: always include top constraints/goals/decisions by recency.
    guard = con.execute(
        "SELECT capsule_id FROM capsule WHERE workspace_id=? AND type IN ('goal','constraint','decision') ORDER BY created_at DESC LIMIT 30",
        (workspace_id,),
    ).fetchall()
    guard_ids = [r["capsule_id"] for r in guard]

    ids = set(guard_ids)

    if query.strip():
        for cid in fts_capsules(con, workspace_id, query, limit=30):
            ids.add(cid)

    if query_vec is not None:
        for cid, _score in vector_top_capsules(con, workspace_id, query_vec, limit=limit):
            ids.add(cid)

    return load_capsules(con, workspace_id, list(ids))
```

---

## 3.7 Deterministic scoring: `sap_core/scoring/scoring.py`

This is the “no-LLM fast pass” you can rely on.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math
import re
import numpy as np
from sap_core.domain.models import Capsule, CapsuleType, EvidenceLevel, GapFinding, MismatchFinding, RareThoughtFinding, Lens


_ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{2,}\b")
_CONFIDENT_WORDS = re.compile(r"\b(must|will|guarantee|always|never|cannot fail)\b", re.IGNORECASE)
_HEDGE_WORDS = re.compile(r"\b(might|may|could|suggests|hypothesis|likely|uncertain)\b", re.IGNORECASE)


EVID_ORDER: Dict[EvidenceLevel, int] = {
    EvidenceLevel.hypothesis: 0,
    EvidenceLevel.estimate: 1,
    EvidenceLevel.simulated: 2,
    EvidenceLevel.measured: 3,
    EvidenceLevel.certified: 4,
}


def evidence_word_level(text: str) -> EvidenceLevel:
    # purely linguistic cue; can be improved.
    if _CONFIDENT_WORDS.search(text):
        return EvidenceLevel.measured
    if _HEDGE_WORDS.search(text):
        return EvidenceLevel.hypothesis
    return EvidenceLevel.estimate


def split_spans(text: str) -> List[Tuple[int, int]]:
    # simple sentence-ish segmentation
    spans = []
    start = 0
    for m in re.finditer(r"[.!?]\s+", text):
        end = m.end()
        spans.append((start, end))
        start = end
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def extract_acronyms(text: str) -> List[Tuple[str, Tuple[int, int]]]:
    out = []
    for m in _ACRONYM_RE.finditer(text):
        out.append((m.group(0), (m.start(), m.end())))
    return out


def build_glossary_index(capsules: List[Capsule]) -> Dict[str, str]:
    idx: Dict[str, str] = {}
    for c in capsules:
        if c.type != CapsuleType.glossary:
            continue
        # convention: "TERM: definition..." or meta["terms"] if present
        if "terms" in c.meta and isinstance(c.meta["terms"], list):
            for t in c.meta["terms"]:
                term = (t.get("term") or "").strip()
                definition = (t.get("definition") or "").strip()
                if term and definition:
                    idx[term.lower()] = definition
        else:
            parts = c.body.split(":", 1)
            if len(parts) == 2:
                idx[parts[0].strip().lower()] = parts[1].strip()
    return idx


def gap_findings(
    draft: str,
    glossary_idx: Dict[str, str],
    recipient_exposure_terms: Optional[Dict[str, float]] = None,
    recipient_actor_id: Optional[str] = None,
) -> List[GapFinding]:
    recipient_exposure_terms = recipient_exposure_terms or {}

    gaps: List[GapFinding] = []

    # Acronym gaps: acronym present but not defined nearby and not known.
    for acr, span in extract_acronyms(draft):
        known = recipient_exposure_terms.get(acr.lower(), 0.0) > 0.5 or (acr.lower() in glossary_idx)
        if not known:
            gaps.append(
                GapFinding(
                    span=span,
                    kind="acronym_unknown",
                    description=f"Acronym '{acr}' likely unknown to recipient.",
                    recipient_actor_id=recipient_actor_id,
                    suggested_bridge=f"{acr} = [define once here].",
                    supporting_capsule_ids=[],
                    confidence=0.75,
                )
            )

    # Glossary term gaps: lens-neutral version (later you can lens-map).
    for term, definition in glossary_idx.items():
        if term in draft.lower():
            seen = recipient_exposure_terms.get(term, 0.0) > 0.5
            if not seen:
                pos = draft.lower().find(term)
                span = (pos, pos + len(term))
                gaps.append(
                    GapFinding(
                        span=span,
                        kind="missing_glossary",
                        description=f"Term '{term}' used; recipient likely hasn't seen its project-specific definition.",
                        recipient_actor_id=recipient_actor_id,
                        suggested_bridge=f"{term} ({definition})",
                        supporting_capsule_ids=[],
                        confidence=0.65,
                    )
                )

    return gaps


def mismatch_findings(
    draft: str,
    constraints: List[Capsule],
    capabilities: List[Capsule],
    expected_evidence: Optional[EvidenceLevel],
) -> List[MismatchFinding]:
    mismatches: List[MismatchFinding] = []

    # Evidence mismatch (linguistic vs expected)
    if expected_evidence is not None:
        stated = evidence_word_level(draft)
        if EVID_ORDER[stated] < EVID_ORDER[expected_evidence]:
            mismatches.append(
                MismatchFinding(
                    span=(0, min(len(draft), 120)),
                    kind="evidence_mismatch",
                    description=f"Draft reads as '{stated.value}' but audience expects at least '{expected_evidence.value}'.",
                    conflicting_capsule_id=None,
                    recommendation="Add uncertainty framing or attach evidence/measurement plan.",
                    confidence=0.72,
                )
            )

    # Constraint conflict: naive lexical match on key phrases (MVP).
    lower = draft.lower()
    for c in constraints:
        key = c.title.lower()
        # heuristic: treat constraint title words as triggers
        if any(w in lower for w in key.split() if len(w) >= 5):
            # not always a conflict; we need negation cues. MVP: look for "use cloud" vs "no cloud".
            if "no cloud" in c.title.lower() and ("cloud" in lower or "hosted" in lower):
                mismatches.append(
                    MismatchFinding(
                        span=(0, min(len(draft), 200)),
                        kind="constraint_conflict",
                        description=f"Potential conflict with constraint: {c.title}",
                        conflicting_capsule_id=c.capsule_id,
                        recommendation="Reframe as local-first alternative or request an exception explicitly.",
                        confidence=0.88,
                    )
                )

    # Capability conflict: bounds in meta (MVP: lead_time_days / certifications / ranges)
    for cap in capabilities:
        meta = cap.meta or {}
        if "lead_time_days" in meta and ("next week" in lower or "tomorrow" in lower):
            mismatches.append(
                MismatchFinding(
                    span=(0, min(len(draft), 200)),
                    kind="capability_conflict",
                    description=f"Timeline wording may conflict with capability lead time ({meta.get('lead_time_days')} days): {cap.title}",
                    conflicting_capsule_id=cap.capsule_id,
                    recommendation="State an achievable schedule or split prototype vs certified production plan.",
                    confidence=0.70,
                )
            )

    return mismatches


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    return float(np.dot(a, b) / denom)


def rare_thought_findings(
    idea_spans: List[Tuple[int, int]],
    idea_vecs: List[List[float]],
    group_centroid_vec: Optional[List[float]],
    goal_centroid_vec: Optional[List[float]],
    draft: str,
) -> List[RareThoughtFinding]:
    if group_centroid_vec is None or goal_centroid_vec is None:
        return []
    g = np.array(group_centroid_vec, dtype=np.float32)
    t = np.array(goal_centroid_vec, dtype=np.float32)

    out: List[RareThoughtFinding] = []
    for (span, vec) in zip(idea_spans, idea_vecs):
        v = np.array(vec, dtype=np.float32)
        novelty = max(0.0, min(1.0, 1.0 - cosine(v, g)))
        relevance = max(0.0, min(1.0, cosine(v, t)))

        if novelty > 0.55 and relevance > 0.40:
            snippet = draft[span[0]:span[1]].strip()
            out.append(
                RareThoughtFinding(
                    span=span,
                    idea_summary=(snippet[:200] + ("..." if len(snippet) > 200 else "")),
                    fit_map=["Relates to current goals/open questions (high semantic overlap)."],
                    protect_notes="Novel viewpoint detected: frame it as a testable option; do not dilute into consensus.",
                    novelty=novelty,
                    relevance=relevance,
                )
            )

    return out
```

---

## 3.8 Prompt templates: `sap_core/prompts/templates.py`

```python
from __future__ import annotations

CAPSULE_EXTRACT_SYSTEM = """You extract *boundary-object capsules* from project text.
Rules:
- Do NOT invent facts. Use only what is in INPUT.
- Output JSON only, matching the schema.
- Propose capsules; do not mark them as published.
- Preserve dissent: if conflicting viewpoints exist, create Position capsules, not "fixes".
"""

CAPSULE_EXTRACT_USER = """<INPUT>
{text}
</INPUT>

Extract candidate capsules relevant to cross-organization collaboration:
- Goal, Constraint, Decision, Glossary, Capability, Assumption, Evidence, Position, OpenQuestion
For each capsule:
- title: short
- body: 1-5 sentences
- lens_tags: subset of [manufacturing, academic, management, policy_outsider]
- evidence_level: one of [hypothesis, estimate, simulated, measured, certified]
- confidence: 0..1
- meta: include structured fields when obvious (e.g., Capability: lead_time_days, certifications)

Return JSON:
{{
  "capsules": [
    {{
      "type": "goal|constraint|decision|glossary|capability|assumption|evidence|position|open_question",
      "title": "...",
      "body": "...",
      "lens_tags": ["..."],
      "evidence_level": "...",
      "confidence": 0.0,
      "meta": {{}}
    }}
  ]
}}
"""

RENDER_MIN_BRIDGE_SYSTEM = """You revise text by inserting minimal bridging context.
Rules:
- Preserve the author's voice. Keep original sentences whenever possible.
- Only add short insertions (1-2 sentences) where needed.
- If you define a term, do it once (parentheses or a short clause).
- Do not remove dissent. If the draft challenges constraints, keep it but add an explicit "exception request" framing.
Output must be JSON only.
"""

RENDER_MIN_BRIDGE_USER = """Target lens: {target_lens}
Max added characters: {max_added_chars}

Known glossary (term -> definition):
{glossary_block}

Guardrails:
Goals:
{goals_block}

Constraints:
{constraints_block}

Decisions:
{decisions_block}

Draft:
<INPUT>
{draft}
</INPUT>

Return JSON:
{{
  "rendered": "...",
  "diff_summary": ["..."],
  "inserted_glossary": ["..."],
  "used_capsule_ids": ["..."]
}}
"""

RENDER_OUTSIDER_SYSTEM = """You produce an outsider/manager/policy-friendly version of a message.
Rules:
- No jargon unless defined once.
- Must include: Purpose, Decision Needed, Options/Tradeoffs, Uncertainty/Evidence level, Next Steps.
- Do NOT claim certainty beyond input evidence.
Output JSON only.
"""

RENDER_OUTSIDER_USER = """Max added characters: {max_added_chars}

Project guardrails (goals/constraints/decisions) in brief:
{guardrails_block}

Draft:
<INPUT>
{draft}
</INPUT>

Return JSON:
{{
  "rendered": "...",
  "diff_summary": ["..."],
  "inserted_glossary": ["..."],
  "used_capsule_ids": ["..."]
}}
"""

CLARIFY_QUESTIONS_SYSTEM = """You generate clarification questions that reduce ambiguity fastest.
Rules:
- 3 to 7 questions.
- Each question must be short and actionable.
- Prefer questions that clarify: evidence level, constraints, timeline, capability bounds, definitions.
Output JSON only.
"""

CLARIFY_QUESTIONS_USER = """Message:
<INPUT>
{text}
</INPUT>

Known constraints/capabilities:
{guardrails_block}

Return JSON:
{{
  "questions": ["..."]
}}
"""

DEBATE_CLUSTER_LABEL_SYSTEM = """You label clusters of ideas neutrally.
Rules:
- Do not take sides.
- Use short labels that outsiders can understand.
Output JSON only.
"""

DEBATE_CLUSTER_LABEL_USER = """Cluster snippets:
{snippets}

Return JSON:
{{"label":"...","key_terms":["...","..."]}}
"""

CONTRADICTION_TESTS_SYSTEM = """You propose minimal discriminating tests for two conflicting claims.
Rules:
- Do not invent specific instruments unless mentioned.
- Prefer measurements/experiments that a manufacturing+academic consortium could agree on.
Output JSON only.
"""

CONTRADICTION_TESTS_USER = """Claim A:
{a}

Claim B:
{b}

Known capabilities:
{capabilities_block}

Return JSON:
{{"tests":["...","..."]}}
"""
```

---

## 3.9 Pipelines (draft analyze + render + message explain)

### `sap_core/pipelines/draft_analyze.py`

```python
from __future__ import annotations
from typing import Dict, List, Optional
import json
from datetime import datetime

from sap_core.domain.models import (
    AlignmentReport, AnalysisMode, CapsuleType, GapFinding, Lens, PolicyConfig
)
from sap_core.retrieval.retrieve import retrieve_bundle
from sap_core.scoring.scoring import build_glossary_index, gap_findings, mismatch_findings


def load_policy(con, workspace_id: str) -> PolicyConfig:
    row = con.execute("SELECT policy_json FROM policy WHERE workspace_id=?", (workspace_id,)).fetchone()
    if not row:
        return PolicyConfig(workspace_id=workspace_id)
    return PolicyConfig(**json.loads(row["policy_json"]))


def recipient_term_exposure(con, workspace_id: str, actor_id: str) -> Dict[str, float]:
    # MVP: build exposure terms by joining glossary capsules the actor has seen.
    rows = con.execute(
        """
        SELECT c.body, c.meta_json
        FROM exposure e
        JOIN capsule c ON c.capsule_id = e.capsule_id
        WHERE e.workspace_id=? AND e.actor_id=? AND c.type='glossary'
        """,
        (workspace_id, actor_id),
    ).fetchall()
    out: Dict[str, float] = {}
    for r in rows:
        meta = json.loads(r["meta_json"] or "{}")
        if "terms" in meta:
            for t in meta["terms"]:
                term = (t.get("term") or "").strip().lower()
                if term:
                    out[term] = max(out.get(term, 0.0), 0.8)
        else:
            body = r["body"]
            parts = body.split(":", 1)
            if parts:
                out[parts[0].strip().lower()] = max(out.get(parts[0].strip().lower(), 0.0), 0.8)
    return out


def decide_policy(report: AlignmentReport, policy: PolicyConfig) -> str:
    max_block = max((b.confidence for b in report.blockers), default=0.0)
    value = max(max_block, 0.4 * len(report.clarity_gaps) / 10.0 + 0.3 * len(report.rare_thoughts) / 10.0)

    if max_block >= policy.blocker_conf_modal:
        return "modal"
    if max_block >= policy.blocker_conf_badge:
        return "badge"
    if value >= policy.hint_value_sidebar:
        return "sidebar"
    return "silent"


def analyze_draft(
    con,
    workspace_id: str,
    draft_text: str,
    recipients: List[str],
    recipient_lenses: List[Lens],
    mode: AnalysisMode,
    query_vec: Optional[List[float]] = None,
) -> AlignmentReport:
    policy = load_policy(con, workspace_id)
    capsules = retrieve_bundle(con, workspace_id, query=draft_text[:600], query_vec=query_vec)

    constraints = [c for c in capsules if c.type == CapsuleType.constraint]
    capabilities = [c for c in capsules if c.type == CapsuleType.capability]
    glossary_caps = [c for c in capsules if c.type == CapsuleType.glossary]
    glossary_idx = build_glossary_index(glossary_caps)

    # Expected evidence depends on lens target; if multiple, take the strictest (max).
    expected = None
    if recipient_lenses:
        levels = [policy.expected_evidence_by_lens.get(l) for l in recipient_lenses]
        levels = [x for x in levels if x is not None]
        if levels:
            order = {"hypothesis":0,"estimate":1,"simulated":2,"measured":3,"certified":4}
            expected = max(levels, key=lambda e: order[e.value])

    all_gaps: List[GapFinding] = []
    for rid in recipients:
        exposure_terms = recipient_term_exposure(con, workspace_id, rid)
        all_gaps.extend(gap_findings(draft_text, glossary_idx, exposure_terms, recipient_actor_id=rid))

    blockers = mismatch_findings(draft_text, constraints, capabilities, expected)

    report = AlignmentReport(
        mode=mode,
        workspace_id=workspace_id,
        recipients=recipients,
        lens_target=recipient_lenses[0] if recipient_lenses else None,
        blockers=blockers,
        clarity_gaps=all_gaps,
        rare_thoughts=[],
        context_capsule_ids=[c.capsule_id for c in capsules],
        policy_decision="silent",
    )
    report.policy_decision = decide_policy(report, policy)
    return report
```

### `sap_core/pipelines/draft_render.py` (LLM optional; if unavailable, degrade)

```python
from __future__ import annotations
from typing import List
import json

from sap_core.domain.models import CapsuleType, Lens
from sap_core.prompts.templates import (
    RENDER_MIN_BRIDGE_SYSTEM, RENDER_MIN_BRIDGE_USER,
    RENDER_OUTSIDER_SYSTEM, RENDER_OUTSIDER_USER
)


def _block(title: str, items: List[str]) -> str:
    if not items:
        return f"{title}: (none)"
    return f"{title}:\n- " + "\n- ".join(items)


def render_draft(
    llm,
    draft: str,
    capsules,
    target_lens: Lens,
    max_added_chars: int = 500,
):
    goals = [c for c in capsules if c.type == CapsuleType.goal]
    constraints = [c for c in capsules if c.type == CapsuleType.constraint]
    decisions = [c for c in capsules if c.type == CapsuleType.decision]
    glossary = [c for c in capsules if c.type == CapsuleType.glossary]

    glossary_block = "\n".join([f"- {g.title}: {g.body}" for g in glossary][:20])
    used_ids = [c.capsule_id for c in (goals + constraints + decisions + glossary)]

    if llm is None:
        # Degraded rendering: return native + tiny appended glossary hints
        extra = ""
        if target_lens == Lens.policy_outsider:
            extra = "\n\n[Purpose]\n...\n[Decision Needed]\n...\n[Tradeoffs]\n...\n[Uncertainty]\n..."
        return {
            "native": draft,
            "rendered": draft + extra,
            "diff_summary": ["LLM unavailable; returned template-only rendering."],
            "inserted_glossary": [],
            "used_capsule_ids": used_ids,
        }

    if target_lens == Lens.policy_outsider:
        guardrails_block = _block("Goals", [g.title for g in goals]) + "\n" + _block("Constraints", [c.title for c in constraints]) + "\n" + _block("Decisions", [d.title for d in decisions])
        prompt = RENDER_OUTSIDER_SYSTEM + "\n\n" + RENDER_OUTSIDER_USER.format(
            max_added_chars=max_added_chars,
            guardrails_block=guardrails_block,
            draft=draft,
        )
    else:
        prompt = RENDER_MIN_BRIDGE_SYSTEM + "\n\n" + RENDER_MIN_BRIDGE_USER.format(
            target_lens=target_lens.value,
            max_added_chars=max_added_chars,
            glossary_block=glossary_block,
            goals_block=_block("Goals", [g.title for g in goals]),
            constraints_block=_block("Constraints", [c.title for c in constraints]),
            decisions_block=_block("Decisions", [d.title for d in decisions]),
            draft=draft,
        )

    raw = llm.generate(prompt, max_tokens=420, temperature=0.2)
    data = json.loads(raw)
    data["native"] = draft
    if "used_capsule_ids" not in data:
        data["used_capsule_ids"] = used_ids
    return data
```

### `sap_core/pipelines/message_explain.py` (fast-pass + optional questions)

```python
from __future__ import annotations
from typing import Optional, List
import json
from sap_core.domain.models import Lens, MessageExplainResponse, SenderLensCard, AlignmentReport, AnalysisMode
from sap_core.pipelines.draft_analyze import analyze_draft


def infer_lens_heuristic(text: str) -> Lens:
    t = text.lower()
    if any(w in t for w in ["yield", "tolerance", "certification", "process", "supplier", "qa"]):
        return Lens.manufacturing
    if any(w in t for w in ["hypothesis", "paper", "citation", "model", "simulate", "reproduc"]):
        return Lens.academic
    if any(w in t for w in ["milestone", "budget", "risk", "timeline", "stakeholder"]):
        return Lens.management
    return Lens.policy_outsider


def explain_message(con, workspace_id: str, message_text: str, recipient_actor_id: Optional[str]) -> dict:
    inferred = infer_lens_heuristic(message_text)

    report: AlignmentReport = analyze_draft(
        con=con,
        workspace_id=workspace_id,
        draft_text=message_text,
        recipients=[recipient_actor_id] if recipient_actor_id else [],
        recipient_lenses=[Lens.management] if recipient_actor_id else [],
        mode=AnalysisMode.after_receive,
        query_vec=None,
    )

    card = {
        "inferred_lens": inferred.value,
        "evidence_style": "mixed (heuristic)",
        "likely_constraints_optimized": [b.conflicting_capsule_id for b in report.blockers if b.conflicting_capsule_id],
        "assumed_prereqs": [g.description for g in report.clarity_gaps[:6]],
        "recommended_questions": [
            "What evidence level supports this claim (hypothesis/simulated/measured/certified)?",
            "Which constraints/capabilities are you optimizing for (cost/yield/certification/timeline)?",
            "What is the smallest test/measurement that would validate the key point?",
        ],
    }

    return {"report": report.model_dump(), "sender_card": card}
```

---

## 3.10 FastAPI app + routes

### `sap_api/app.py`

```python
from __future__ import annotations
from fastapi import FastAPI
from sap_store.sqlite.migrate import apply_all

from sap_api.routes.health import router as health_router
from sap_api.routes.workspace import router as workspace_router
from sap_api.routes.ingest import router as ingest_router
from sap_api.routes.capsule import router as capsule_router
from sap_api.routes.draft import router as draft_router
from sap_api.routes.message import router as message_router
from sap_api.routes.ideas import router as ideas_router
from sap_api.routes.exposure import router as exposure_router
from sap_api.routes.trust import router as trust_router
from sap_api.routes.sync import router as sync_router


def create_app() -> FastAPI:
    apply_all()
    app = FastAPI(title="SAP", version="0.2")
    app.include_router(health_router)
    app.include_router(workspace_router)
    app.include_router(ingest_router)
    app.include_router(capsule_router)
    app.include_router(draft_router)
    app.include_router(message_router)
    app.include_router(ideas_router)
    app.include_router(exposure_router)
    app.include_router(trust_router)
    app.include_router(sync_router)
    return app


app = create_app()
```

### `sap_api/deps.py`

```python
from __future__ import annotations
from sap_store.sqlite.db import db_session
from sap_core.domain.models import PolicyConfig
import json

def get_con():
    with db_session() as con:
        yield con
```

(Keep it simple. If you want async + pooling later, swap this dependency.)

---

### Minimal routes: `sap_api/routes/draft.py`

```python
from __future__ import annotations
from fastapi import APIRouter, Depends
from typing import Optional, List
import ulid

from sap_api.deps import get_con
from sap_core.domain.models import DraftAnalyzeRequest, DraftRenderRequest
from sap_core.pipelines.draft_analyze import analyze_draft
from sap_core.retrieval.retrieve import retrieve_bundle
from sap_models.router import ModelRouter
from sap_models.llm import LocalLLM

router = APIRouter(prefix="/v1/draft", tags=["draft"])

# MVP: configure here; later inject via config file.
_router = ModelRouter(allow_llm_on_typing=False, allow_llm_before_send=True)
_llm = None  # set to LocalLLM("...gguf...") if installed


@router.post("/analyze")
def analyze(req: dict, con=Depends(get_con)):
    # Accept dict to avoid repeating model types here; validate lightly.
    workspace_id = req["workspace_id"]
    draft_text = req["draft_text"]
    recipients = req.get("recipients", [])
    recipient_lenses = req.get("recipient_lenses", [])
    mode = req.get("mode", "before_send")

    # embedding optional; you can add embedder later and pass query_vec.
    report = analyze_draft(
        con=con,
        workspace_id=workspace_id,
        draft_text=draft_text,
        recipients=recipients,
        recipient_lenses=[r for r in recipient_lenses],  # Lens values in string accepted upstream
        mode=mode,
        query_vec=None,
    )
    return report.model_dump()


@router.post("/render")
def render(req: dict, con=Depends(get_con)):
    workspace_id = req["workspace_id"]
    draft_text = req["draft_text"]
    target_lens = req["target_lens"]
    max_added_chars = req.get("max_added_chars", 500)

    capsules = retrieve_bundle(con, workspace_id, query=draft_text[:600], query_vec=None)
    out = __import__("sap_core.pipelines.draft_render", fromlist=["render_draft"]).render_draft(
        llm=_llm,
        draft=draft_text,
        capsules=capsules,
        target_lens=target_lens,
        max_added_chars=max_added_chars,
    )
    return out
```

(Other routes are similar; you can keep them small by calling pipeline modules.)

---

# 4) “All prompts” + “all scoring” are already included above — but here’s the missing piece: **Idea Map** + **Summarize by lens** (deterministic + LLM-labeled)

## 4.1 Idea map pipeline: `sap_core/pipelines/ideas_map.py`

```python
from __future__ import annotations
from typing import List, Optional, Dict, Any
import json
import numpy as np
from sklearn.cluster import KMeans

from sap_core.domain.models import CapsuleType


def ideas_map(con, workspace_id: str, query: Optional[str] = None, limit_chunks: int = 400) -> dict:
    # Pull chunks (FTS if query; else most recent)
    if query:
        rows = con.execute(
            "SELECT chunk_id, text FROM fts_chunks WHERE fts_chunks MATCH ? AND workspace_id=? LIMIT ?",
            (query, workspace_id, limit_chunks),
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT chunk_id, text FROM chunk WHERE workspace_id=? ORDER BY created_at DESC LIMIT ?",
            (workspace_id, limit_chunks),
        ).fetchall()

    chunk_ids = [r["chunk_id"] for r in rows]
    texts = [r["text"] for r in rows]

    # Pull embeddings (must exist for meaningful clustering)
    emb_rows = con.execute(
        "SELECT owner_id, vec_json FROM embedding WHERE workspace_id=? AND owner_type='chunk'",
        (workspace_id,),
    ).fetchall()
    vec_map = {r["owner_id"]: np.array(json.loads(r["vec_json"]), dtype=np.float32) for r in emb_rows}
    vecs = [vec_map.get(cid) for cid in chunk_ids if cid in vec_map]
    kept_ids = [cid for cid in chunk_ids if cid in vec_map]

    if len(vecs) < 10:
        return {
            "workspace_id": workspace_id,
            "query": query,
            "clusters": [],
            "stance_axes": [],
            "contradiction_seeds": [],
            "outlier_seeds": kept_ids[:20],
        }

    X = np.vstack(vecs)
    k = max(2, min(8, len(vecs)//40))
    km = KMeans(n_clusters=k, n_init="auto", random_state=7)
    labels = km.fit_predict(X)

    clusters = []
    for i in range(k):
        members = [kept_ids[j] for j in range(len(kept_ids)) if labels[j] == i]
        clusters.append({
            "cluster_id": f"cl_{i}",
            "label": f"Cluster {i}",
            "capsule_ids": [],
            "chunk_ids": members[:120],
            "centroid_terms": [],
        })

    # Stance axes: use Position capsules as anchors (MVP: list them)
    pos = con.execute(
        "SELECT capsule_id, title, body, meta_json FROM capsule WHERE workspace_id=? AND type='position' ORDER BY created_at DESC LIMIT 20",
        (workspace_id,),
    ).fetchall()

    stance_axes = []
    if len(pos) >= 2:
        stance_axes.append({
            "axis_id": "axis_0",
            "topic": "Position landscape (MVP)",
            "pole_a_label": pos[0]["title"],
            "pole_b_label": pos[1]["title"],
            "supporting_position_capsules_a": [pos[0]["capsule_id"]],
            "supporting_position_capsules_b": [pos[1]["capsule_id"]],
        })

    return {
        "workspace_id": workspace_id,
        "query": query,
        "clusters": clusters,
        "stance_axes": stance_axes,
        "contradiction_seeds": [],
        "outlier_seeds": [],
    }
```

## 4.2 Summarize by lens: `sap_core/pipelines/ideas_summarize.py`

```python
from __future__ import annotations
from typing import Optional
from sap_core.domain.models import Lens
from sap_core.prompts.templates import RENDER_OUTSIDER_SYSTEM, RENDER_OUTSIDER_USER

def summarize_by_lens(llm, text: str) -> dict:
    if llm is None:
        # deterministic fallback
        return {
            "manufacturing": "LLM unavailable: summarize focusing on yield/tolerance/certification/lead time.",
            "academic": "LLM unavailable: summarize focusing on hypotheses/assumptions/evidence/next experiments.",
            "management": "LLM unavailable: summarize focusing on scope/milestones/risks/decisions needed.",
            "policy_outsider": "LLM unavailable: summarize focusing on purpose/tradeoffs/uncertainty/accountability.",
        }

    def one(lens: Lens) -> str:
        prompt = RENDER_OUTSIDER_SYSTEM + "\n\n" + RENDER_OUTSIDER_USER.format(
            max_added_chars=800,
            guardrails_block=f"(Summarize as {lens.value})",
            draft=text,
        )
        raw = llm.generate(prompt, max_tokens=520, temperature=0.15)
        import json
        return json.loads(raw)["rendered"]

    return {
        "manufacturing": one(Lens.manufacturing),
        "academic": one(Lens.academic),
        "management": one(Lens.management),
        "policy_outsider": one(Lens.policy_outsider),
    }
```

---

# How you run it (MVP)

1. Install:

```bash
pip install -e .
# optional:
pip install -e ".[models]"
```

2. Start server:

```bash
uvicorn sap_api.app:app --host 127.0.0.1 --port 8787
```

3. Create workspace, ingest, analyze drafts via the API.

---

# What you’ll likely want next (immediate improvements)

* Swap embedding JSON vectors → **sqlite-vec** (for speed + storage)
* Make `/draft/analyze` accept **query_vec** by wiring the embedder
* Add the **job worker** (capsule extraction + profile updates)
* Add signing + redaction hooks (publish/sync)

If you want, paste your preferred deployment target (macOS-only daemon, Linux server inside company LAN, or both) and I’ll adapt the **default config**, socket choice (localhost vs unix socket), and packaging (systemd/launchd) accordingly.
