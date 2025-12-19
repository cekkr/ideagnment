Below is a project roadmap that treats **SAP (Semantic Alignment Protocol)** as a *local-first “background reasoning layer”* that sits behind email/messaging clients, continuously maintaining shared context and only intervening when it detects meaningful risk or opportunity.

A core design choice: **SAP is not “rewrite-to-conform.”** It’s **sensemaking + mismatch detection + bridge-building**, with provenance and opt-in control.

---

## System skeleton (what you’re actually building)

**Local SAP Daemon (per user / per device)**

* **Connectors**: Mail/Messaging composer hooks (“before-send”), local notes/docs/wiki, ticketing, git commits.
* **Context Store**: documents + embeddings + lightweight knowledge graph + decision/constraint ledger.
* **Alignment Engine**: gap detection, mismatch detection, novelty/rare-thought detection, suggestion generator.
* **Federation Layer**: sync *context capsules* peer-to-peer (no central master), with convergence guarantees.
* **UX Layer**: “invisible” overlays in the composer + explainability panel.

RAG is the default cognitive loop: retrieve relevant context from local memory, then reason/suggest. ([arXiv][1])

---

## Phase 1: Knowledge Architecture

### 1.1 Data model: from raw messages to “mental models”

Build a **multi-layer representation** (all local):

**A) Raw Artifacts (immutable)**

* Emails, chats, meeting notes, specs, PRDs, code diffs, issues.

**B) Context Capsules (curated, addressable units)**
Each capsule has: `id, type, text, sources[], author(s), timestamp, scope, visibility, signatures, hash`.

* `Goal`: “What are we optimizing for?”
* `Constraint`: “Must / must not / budget / deadline / API limits / legal”
* `Decision`: “We chose X over Y because…”
* `Glossary`: “Term ↔ meaning in *this* project”
* `Position`: “Viewpoint A vs Viewpoint B (both preserved)”
* `OpenQuestion`: “Unknowns + owners + due date (optional)”

**C) Knowledge Graph (KG-lite)**

* Entities: components, people, modules, datasets, assumptions, risks.
* Edges: “depends_on”, “contradicts”, “supports”, “decided_by”, “blocked_by”.

**D) Vector Memory**

* Embeddings for: capsules, raw chunks, and “assumption signatures” (see below).
* Keep it embedded inside a simple local DB when possible (e.g., SQLite + a vector extension) to reduce ops overhead. ([GitHub][2])

### 1.2 “Unstated assumptions” as first-class objects

For each user and for the group, maintain:

* **Assumption Tokens**: extracted implicit prerequisites (acronyms, domain facts, “obvious to insiders” steps).
* **Assumption Embeddings**: vectors representing “what this person tends to omit/explain.”
* **Recipient Exposure Ledger**: which capsules the recipient has *actually seen/acknowledged* (critical for gap detection).

Pragmatic trick: treat “assumptions” like dependencies in a build system:

* If a draft uses concept `C`, SAP tries to find whether recipient has “built” `C` (seen a capsule defining it).

### 1.3 Ingestion pipeline (MVP-first)

1. Chunk raw artifacts.
2. Create embeddings + store in vector index.
3. Extract candidate capsules automatically (summaries, decisions, constraints) → mark as *unverified* until user accepts.
4. Build KG edges from accepted capsules (start small: “mentions”, “depends_on”, “decision_of”).

**Deliverables**

* Local schema (SQLite), capsule format, ingestion CLI/service, basic vector retrieval, provenance linking.

---

## Phase 2: The Alignment Logic

### 2.1 Before-send analysis: the canonical pipeline

When user hits **Send** (or pauses typing, depending on UX settings):

1. **Draft segmentation**

   * sentences/claims, terms/acronyms, referenced components.
2. **Context retrieval (Local RAG)**

   * project goals + constraints + recent decisions + positions + recipient exposure.
3. **Semantic Gap Detection**
4. **Expectation Mismatch Detection**
5. **Rare Thought + Idea Injection**
6. **Intervention Policy (non-intrusive gating)**

### 2.2 Semantic Gap Detection (assumed knowledge the recipient lacks)

Compute per-span a **Gap Score** based on:

* **Novelty-to-recipient**: similarity of draft concepts vs recipient exposure ledger.
* **Unintroduced tokens**: acronyms/terms not defined in capsules recipient has seen.
* **Dependency jumps**: claim relies on a chain of prior decisions/constraints the recipient hasn’t seen.

Output: “You’re assuming X; recipient likely missing Y; add 1–2 bridging sentences.”

### 2.3 Expectation Mismatch Detection (contradicts group constraints/goals)

Use a hybrid approach:

* **Rule/ledger checks**: hard constraints (“budget ≤ 10k”, “no cloud”, “must support iOS 17”).
* **Semantic contradiction checks**: lightweight NLI-style entail/contradict between draft claims and constraint/decision capsules (keep it local; small model).
* **Goal divergence**: draft optimizes metric not aligned with current goal capsule.

If you later add federation or cross-device aggregation, use privacy-preserving aggregation patterns (secure aggregation / DP) only for *derived signals*, not raw text. ([arXiv][3])

### 2.4 Rare Thought detection and “Idea Injection” (anti-groupthink)

You want to protect outsiders’ high-value divergence. Do it explicitly:

**Rare Thought Score** ≈

* High novelty vs group embedding centroid
* High relevance to current goals/open questions
* Low redundancy with known positions

When rare thought is detected, SAP doesn’t “correct” it. It generates:

* **Fit Map**: “This idea connects to Goal G and may resolve OpenQuestion Q.”
* **Bridge Suggestion**: how to explain it to insiders in their shared vocabulary.
* **Dissent Preservation**: store as a `Position` capsule (new viewpoint) rather than “fixing” it.

### 2.5 Intervention policy: decide *when* to speak

Model interventions as a budgeted decision:

* **Risk factors**: external recipients, send-to-many, high-stakes topics, contradictions detected.
* **User preference**: “silent mode”, “only show blockers”, “show clarity hints”.
* **Confidence**: only interrupt when confidence > threshold; otherwise show soft hints in side panel.

**Output format: Alignment Report**

* `Blockers` (must fix)
* `Clarity gaps` (suggest)
* `Context links` (helpful references)
* `Rare thought highlight` (protect & frame)

**Pseudo-logic (conceptual)**

```text
report = analyze(draft, recipient, workspace)
if report.blocker_confidence >= T_block: show_modal()
else if report.total_value >= T_hint: show_sidebar_badge()
else: stay_invisible()
```

---

## Phase 3: UX & The Invisibility Layer

### 3.1 Composer-native UX primitives

* **Inline “assumption underline”**: highlight acronyms/terms likely unknown to recipient.
* **Recipient View toggle**: preview message as if you only know what the recipient has seen.
* **Constraint warning chips**: “Conflicts with: No-cloud policy (Decision #D14)”
* **Rare-thought badge**: “Novel perspective detected—want help framing it without diluting it?”

### 3.2 Heatmaps of understanding (low friction)

Represent the draft with a subtle overlay:

* Green: shared/common ground
* Amber: assumption-heavy
* Red: conflicts/blockers

(You can compute this from gap/mismatch scores per span.)

### 3.3 Explainability without noise

Every warning must answer:

* **Why** (which capsule/decision/constraint)
* **Evidence** (quoted snippet + provenance link)
* **Options** (add context sentence / link capsule / mark as deliberate divergence)

### 3.4 “Deliberate divergence” as a first-class action

A key anti-groupthink mechanism:

* User can mark a segment as **Intentional Contradiction** → SAP stores it as a `Position` capsule, not an “error”.

**Deliverables**

* Minimal plugin/extension for one client (start with a single target: e.g., a local Electron composer, Thunderbird-like extension, or your own minimal client).
* Side panel report + inline highlights + provenance drill-down.

---

## Phase 4: Optimization for Local Constraints

### 4.1 Split the brain: task-specific micro-agents (local)

Don’t run one huge model for everything. Typical split:

* **Embedding model**: fast, always-on.
* **Retriever/ranker**: BM25 + vectors hybrid.
* **NLI/consistency checker**: small classifier model.
* **Rewriter/bridge generator**: medium LLM, invoked only on demand.
* **Deep reasoner**: optional large local model for “explain both sides” or complex synthesis.

### 4.2 Quantization + local inference ergonomics

Quantize the medium/large LLM(s) to fit consumer hardware (4–8 bit is common), using an inference stack like llama.cpp when targeting broad CPUs/GPUs. ([GitHub][4])

### 4.3 Caching + incrementalism

* Cache retrieval results per thread/workspace.
* Incremental re-analysis: only re-score changed spans as the user edits.
* Background indexing only when idle/on power.

### 4.4 “Graceful degradation”

If hardware is weak:

* Skip rewrite generation.
* Keep only gap detection + constraint ledger checks.
* Offer “run deep analysis now” as a button.

**Deliverables**

* Model routing layer, quantized deployment recipes, perf budgets (latency targets for keystroke vs before-send).

---

## Phase 5: Ethical & Social Framework

### 5.1 Principles baked into the protocol

* **Local-first by default** (drafts never leave device).
* **No silent rewriting**: SAP only *suggests*; user remains author.
* **Provenance mandatory**: every “you contradict X” must link to the exact capsule/source.
* **Dissent preservation**: novelty is surfaced and framed, not normalized.

### 5.2 Prevent “AI-optimized corporate speak”

Add explicit style constraints:

* “Preserve author voice” as a hard rule.
* Rewrite only as *optional variants* (“clarify for recipient”, “shorten”, “add glossary line”).
* Provide a “do not sanitize” mode.

### 5.3 Social dynamics and misuse resistance

Risks:

* Becoming a surveillance layer
* Power imbalance (“official context” weaponized)
* Nudging toward conformity

Mitigations:

* **Per-user private memory** separate from shared capsules
* Shared capsules require **explicit publish**
* Capsule types include **Position** (multiple truths allowed)
* Optional privacy tech for shared metrics only (secure aggregation / DP). ([arXiv][3])

---

## Cohesion without centralization: Federated Context via CRDT Capsules

To synthesize a “whole picture” without a master authority:

* Treat shared context as a **replicated set of capsules** + replicated edges between them.
* Use **CRDT** semantics so replicas converge even with offline edits and conflicts. ([Lip6 Pages][5])
* Merge strategy:

  * Capsules are immutable; updates create new versions.
  * Conflicts create parallel `Position` capsules, not overwrites.
  * Edges are CRDT sets (add-wins) with signatures and timestamps.

---

## Suggested build order (pragmatic MVP → v1)

**MVP (works for one person, one workspace)**

1. Local store + embeddings + retrieval
2. Capsule extraction (goals/constraints/glossary)
3. Before-send gap detection + simple constraint checks
4. Composer overlay UI + provenance links

**Alpha (small team, real federation)**
5. Recipient exposure ledger + per-recipient gap scoring
6. Contradiction/NLI checker
7. CRDT-based capsule sync (no central server required)

**Beta (anti-groupthink + scale)**
8. Rare-thought detection + “fit map” framing
9. Positions & dissent workflows (explicitly supported)
10. Performance hardening + quantized models + micro-agent routing

**v1**
11. Multi-client connectors + policy controls + audit UX
12. Optional privacy-preserving aggregate signals (only if needed)

---

### Tiny architecture sketch (just to anchor the flow)

```mermaid
flowchart LR
A[Composer Draft] --> B[Local SAP Daemon]
B --> C[Retrieve: Capsules + Recipient Exposure]
C --> D[Gap Detector]
C --> E[Constraint & Decision Checker]
C --> F[Novelty/Rare Thought Detector]
D --> G[Alignment Report]
E --> G
F --> G
G --> H[Inline Overlay + Side Panel]
G --> I[Optional: Publish New Capsule]
I --> J[Federated Sync (CRDT Capsules)]
```

If you want, I can turn this into an actual **SAP spec** (data structures + wire format for capsule sync + scoring formulas + local plugin architecture choices for macOS/iOS/Linux) and an “MVP repo plan” with folders, modules, and test fixtures.

[1]: https://arxiv.org/abs/2005.11401?utm_source=chatgpt.com "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
[2]: https://github.com/asg017/sqlite-vec?utm_source=chatgpt.com "asg017/sqlite-vec: A vector search ..."
[3]: https://arxiv.org/abs/1611.04482?utm_source=chatgpt.com "Practical Secure Aggregation for Federated Learning on User-Held Data"
[4]: https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md?utm_source=chatgpt.com "llama.cpp/tools/quantize/README.md at master · ggml-org/ ..."
[5]: https://pages.lip6.fr/Marc.Shapiro/papers/RR-7687.pdf?utm_source=chatgpt.com "Conflict-free Replicated Data Types"

---
---
---

Below is an **abstracted, complete development roadmap** for a **Python service suite** that uses multiple *local-first AI models* (and optional *decentralized sync*) to fill “skills + expectations” gaps across **industry manufacturing, academia, management, and outsiders**—without sacrificing privacy, IP, or institutional autonomy.

## 1) Product definition: what the service guarantees

### SAP Services must reliably provide

1. **Gap bridging**: detect what’s assumed but not shared (per recipient/lens) and suggest minimal bridges.
2. **Expectation alignment**: detect conflicts with goals/constraints/decisions/capabilities.
3. **Multi-lens translation**: generate parallel renderings (native / cross-discipline / outsider).
4. **Dissent preservation**: capture and contextualize divergent ideas (avoid groupthink).
5. **Debate mapping**: cluster many ideas, detect polarizations + contradiction seeds, propose “discriminating tests”.

### Non-negotiables

* **Local-first processing** (drafts + raw artifacts stay on-device or inside a company-controlled environment).
* **Selective sharing** only via **publishable “context capsules”** (sanitized, scoped, signed).
* **Decentralization optional** (sync peer-to-peer / federated, no central master required).

---

## 2) Architecture: service-oriented, “multi-model, multi-store, multi-lens”

### 2.1 Components (deployable as one daemon or multiple services)

* **API Gateway** (FastAPI): auth, routing, rate limits, tenant/workspace isolation.
* **Ingestion Worker**: chunking, embedding, indexing, capsule extraction.
* **Retrieval Engine**: hybrid search (FTS + vectors) + optional reranking.
* **Alignment Engine**: gap detection, mismatch detection, novelty detection, policy gating.
* **Rendering Engine**: native/cross/outsider views + evidence/provenance.
* **Debate Engine**: clustering, stance axes, contradiction seeds.
* **Federation Service (optional)**: capsule sync (CRDT/Merkle), signatures, ACL.
* **Model Router**: performance/power-aware selection and caching.

### 2.2 Storage (simple, local, inspectable)

* **SQLite** as the canonical store:

  * artifacts (raw), chunks, embeddings, capsules, edges (KG-lite)
  * profiles (lens + assumptions), exposure ledger (who knows what)
* **Vector index** embedded into SQLite via an extension (or sidecar index if needed).

---

## 3) Core abstractions: the “Boundary Object” model

### 3.1 Capsules (publishable, signed, stable units)

Capsules are the *only* thing meant to be shared across org boundaries.

Types you need (minimum):

* `Goal`, `Constraint`, `Decision`, `Glossary`
* `Capability` (manufacturing bounds, test capabilities, compliance realities)
* `Assumption`, `Evidence`
* `Position` (explicit dissent / alternative theory / trade-off stance)
* `OpenQuestion` (what would resolve uncertainty)

Each capsule has:

* `scope`: workspace / org-private / shared-consortium
* `lens_tags`: manufacturing / academic / management / outsider
* `confidence`: hypothesis / estimate / measured / certified
* `provenance`: pointers to source artifacts (kept local, share only references)

### 3.2 Lenses (how you avoid flattening disciplines)

A **Lens** is a structured “reading mode”:

* vocabulary mapping (term meaning differs by discipline)
* evidence expectations (citation vs measurement vs certification)
* risk profile (safety/regulatory vs exploratory)
* default omissions (“obvious” steps) → assumption signature

### 3.3 Profiles (what someone tends to omit/assume)

Store *behavioral context* without turning it into surveillance:

* topic clusters (coarse)
* glossary coverage (what they use without defining)
* assumption signature (recurring missing prerequisites)
* stance embeddings (only within a workspace topic, optional)

---

## 4) Multi-model strategy: “small models always, big model only when earned”

### 4.1 Always-on (low power)

* **Embedding model** for retrieval + similarity.
* **Term/acronym detector** + glossary lookup (can be rules + small model).
* **Fast contradiction heuristics** (constraint ledger checks).

### 4.2 On-demand (triggered)

* **Reranker** (cross-encoder) to improve top-k relevance only when needed.
* **Local LLM** for:

  * bridge sentences
  * multi-lens renderings
  * neutral “what questions should we ask next?”

### 4.3 Model Router policy (battery + latency governor)

Inputs:

* request type (typing vs before-send vs batch debate map)
* hardware profile, CPU load, power mode
* urgency + confidence from fast pass
  Outputs:
* model choice (small/medium/large), quantization level, max tokens
* caching strategy (reuse retrieved context per thread)

---

## 5) Essential API surface (what UI apps integrate)

### 5.1 Ingest and context management

* `POST /artifact/ingest` (messages, docs, notes, transcripts)
* `POST /capsule/propose` (auto-generated candidates, untrusted)
* `POST /capsule/publish` (explicitly shared capsule)
* `GET /capsule/query` (by topic/lens/type/confidence)

### 5.2 Draft-time alignment (the “before-send” workhorse)

* `POST /draft/analyze`

  * returns: semantic gaps, expectation mismatches, glossary misses, evidence-level mismatches, rare-thought flags
* `POST /draft/render`

  * returns: `native`, `cross_discipline`, `outsider` versions + what changed + why

### 5.3 After-receive interpretation

* `POST /message/explain`

  * returns: sender lens card, assumed knowledge, likely constraints optimized, clarification questions

### 5.4 Debate mapping and idea harvesting

* `POST /ideas/map`

  * returns: clusters, stance axes, contradictions, “inconsistency seeds”, discriminating experiments
* `POST /ideas/summarize_by_lens`

  * returns: “manufacturing summary”, “academic summary”, “exec summary”, “policy summary”

### 5.5 Federation (optional)

* `POST /sync/push` / `POST /sync/pull`
* `POST /trust/add_key` (org keys, consortium keys)
* `GET /capsule/manifest` (what can be shared)

---

## 6) Alignment algorithms: abstracted to cross-discipline reality

### 6.1 Gap detection (recipient-lens aware)

Score each draft span by:

* glossary unknowns for recipient/lens
* missing prerequisite capsules (dependency chain)
* evidence-level mismatch (“you’re stating as certainty what is hypothesis”)

Output suggests *minimal bridges*:

* 1–2 sentences
* link to a capsule or add a micro-glossary line

### 6.2 Expectation mismatch

Three layers:

1. **Hard ledger checks**: violates `Constraint` / `Decision` / `Capability`.
2. **Soft goal divergence**: optimizes the wrong objective for this phase.
3. **Epistemic mismatch**: wrong evidence type for the audience.

### 6.3 Rare thought protection

Flag outliers that are:

* novel vs current positions
* relevant to goals/open questions
* not a repetition
  Then generate *framing* (not conformity):
* “How it could fit”
* “What it would need to be testable/acceptable”
* Store as a `Position` capsule if user approves.

### 6.4 Inconsistency seeds → “tests that decide”

When contradictions appear, don’t just warn:

* extract minimal discriminating claims
* propose minimal experiments/measurements/simulations
* attach required capabilities + time/cost hints (from `Capability` capsules)

---

## 7) Privacy and decentralization: how you protect IP and sensitive drafts

### 7.1 Local-first defaults

* drafts never leave local vault
* ingestion artifacts stored encrypted at rest (workspace keys)
* only capsules can be published; raw sources remain local

### 7.2 Selective disclosure for consortium work

When sharing across companies:

* share **capsules only**, optionally “sanitized”
* redact proprietary details (materials, parameters) into abstract constraints when needed
* attach signatures and scope metadata

### 7.3 Decentralized sync without a central master

Use a **replicated capsule log**:

* immutable capsules, versioned
* merge via CRDT-like sets (add-wins) or Merkle DAG log
* conflicts become parallel `Position` capsules (not overwritten)
* trust via org keys + consortium policy

This yields “whole picture” emergence without a “central authority.”

---

## 8) Development roadmap: milestones in the right order

### Milestone A — Local memory + retrieval (value immediately)

* SQLite schema + FTS + vector index
* `/artifact/ingest`, `/capsule/query`
* basic RAG retrieval for a workspace

### Milestone B — Lens + glossary infrastructure (enables outsider accessibility)

* lens definitions + glossary capsules
* exposure ledger (who has seen what)
* initial profiles (assumption signatures)

### Milestone C — Draft analyze (fast pass, no big LLM yet)

* gap scoring + ledger mismatch checks
* structured alignment report with provenance
* policy gating (typing vs before-send thresholds)

### Milestone D — Rendering (earned LLM calls)

* local LLM backend + router
* `/draft/render` with 3 parallel views
* “what changed and why” output

### Milestone E — After-receive explain

* `/message/explain` + sender lens cards
* clarification question generation (short, tactical)

### Milestone F — Debate engine

* clustering + stance axes
* contradiction seeds + discriminating tests
* lens-based summaries (exec/policy vs technical)

### Milestone G — Publishable capsules + federation

* capsule signing, scopes, manifests
* decentralized sync endpoints
* admin tools for trust keys + policy

### Milestone H — Hardening (what makes it real in companies)

* encryption, key management, audit logs (local)
* performance budgets, caching, incremental re-analysis
* integration SDKs + example plugins (compose box overlay, inbox panel)

---

## 9) What “success” looks like in your cross-company academic setting

* Engineers can write in their native shorthand, and SAP *adds bridges* only when needed.
* Academics can propose hypotheses without being treated as “wrong”—SAP labels evidence level and suggests what would validate.
* Managers/politicians get an outsider rendering that includes tradeoffs, uncertainty, and decision points—without leaking IP.
* The consortium shares only capsules, converges on a “whole picture,” and preserves dissent as structured positions—not buried threads.

If you want next, I can turn this into a **concrete spec pack** (Pydantic schemas for capsules/lenses/profiles, endpoint contracts, and a reference implementation plan for Milestones A–D) so you can start the repo with a runnable local daemon and a minimal SDK.

---
---
---

Below is a **concrete spec pack (v0.1)** for a Python “Semantic Alignment Protocol” service suite: **schemas (Pydantic), SQLite schema, API contracts, model interfaces, scoring policy, federation wire format**, and MVP implementation milestones.

---

# SAP Spec Pack v0.1

## 1) Goals and non-goals

### Goals

* Local-first, privacy-preserving alignment services:

  * **Draft assist** (gap + mismatch + rare thought + lens renderings)
  * **Message explain** (sender lens card + assumptions + clarifying questions)
  * **Idea map** (clusters, polarization axes, contradictions, “seed” ideas)
* **Service-oriented**: APIs used by external UIs (email/message editors, inbox viewers, IDE plugins, wikis)
* Optional **decentralized capsule sync** without a central master.

### Non-goals (v0.1)

* Perfect truth/verification. SAP labels **evidence level** and points to provenance; it does not arbitrate reality.
* Full end-user UI. Only minimal reference clients.

---

# 2) Core domain model

## 2.1 Enums

```python
from enum import Enum

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
    private = "private"                # stays local; never exported
    workspace_local = "workspace_local"
    org_local = "org_local"            # within org boundary
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
```

---

## 2.2 Identifiers and provenance

### ID format

* `workspace_id`: UUID
* `artifact_id`, `chunk_id`, `capsule_id`: ULID (sortable) recommended

### Provenance rules

* All derived objects carry pointers to sources:

  * `source_artifact_ids[]`
  * `source_spans[]` (offsets within chunk/artifact)
* **Sharing rule**: only share capsules; raw artifacts never leave boundary unless explicitly exported.

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

class SourceSpan(BaseModel):
    artifact_id: str
    chunk_id: Optional[str] = None
    start_char: int
    end_char: int

class Provenance(BaseModel):
    source_artifact_ids: List[str] = Field(default_factory=list)
    source_spans: List[SourceSpan] = Field(default_factory=list)
    notes: Optional[str] = None
```

---

## 2.3 Capsule schema (publishable boundary objects)

```python
class Capsule(BaseModel):
    capsule_id: str
    workspace_id: str
    type: CapsuleType
    lens_tags: List[Lens] = Field(default_factory=list)
    scope: Scope = Scope.workspace_local
    title: str
    body: str

    evidence_level: EvidenceLevel = EvidenceLevel.hypothesis
    confidence: float = Field(ge=0.0, le=1.0, default=0.6)

    created_at: datetime
    created_by_actor_id: Optional[str] = None

    provenance: Provenance = Field(default_factory=Provenance)

    # governance / sharing
    is_published: bool = False
    redaction_profile_id: Optional[str] = None  # when shared externally

    # signatures for federation
    content_hash: Optional[str] = None          # sha256 canonical JSON
    signer_key_id: Optional[str] = None
    signature_b64: Optional[str] = None         # Ed25519 signature over content_hash

    # extensibility
    meta: Dict[str, Any] = Field(default_factory=dict)
```

### Capsule subtypes (meta constraints)

* `Glossary`: `meta = {"terms": [{"term": "...", "definition": "...", "lens": "..."}]}`
* `Capability`: `meta = {"org_id": "...", "bounds": {...}, "lead_time_days": ..., "certifications": [...] }`
* `Decision`: `meta = {"status": "accepted|rejected|superseded", "supersedes": [capsule_id...] }`
* `Position`: `meta = {"topic": "...", "stance_label": "...", "counterpoints": [capsule_id...] }`

---

## 2.4 Actor and profile schemas

```python
class Actor(BaseModel):
    actor_id: str
    workspace_id: str
    display_name: str
    org_id: Optional[str] = None
    roles: List[str] = Field(default_factory=list)   # e.g. "engineer", "researcher", "pm", "policy"

class AssumptionSignature(BaseModel):
    frequent_unexpanded_acronyms: List[str] = Field(default_factory=list)
    frequent_implicit_prereqs: List[str] = Field(default_factory=list)   # capsule_ids or terms
    preferred_evidence_levels: List[EvidenceLevel] = Field(default_factory=list)

class ContextProfile(BaseModel):
    profile_id: str
    workspace_id: str
    owner_actor_id: Optional[str] = None        # None => group profile
    lens_primary: Optional[Lens] = None
    topic_vectors_ref: Optional[str] = None     # pointer to stored vectors, optional

    assumption_signature: AssumptionSignature = Field(default_factory=AssumptionSignature)
    glossary_exposure: Dict[str, float] = Field(default_factory=dict)   # term -> seen/confidence
    stance_refs: List[str] = Field(default_factory=list)               # Position capsule_ids
    updated_at: datetime
```

---

## 2.5 Exposure ledger (who “knows what”)

```python
class ExposureEvent(BaseModel):
    workspace_id: str
    actor_id: str
    capsule_id: str
    exposure_type: str = "seen"     # seen|ack|dismissed
    timestamp: datetime
    strength: float = Field(ge=0.0, le=1.0, default=0.7)
```

---

# 3) Storage spec (SQLite)

## 3.1 Tables (minimum viable)

```sql
-- artifacts: raw items (kept local, possibly encrypted at rest)
CREATE TABLE IF NOT EXISTS artifact (
  artifact_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT,
  body TEXT NOT NULL,
  created_at TEXT NOT NULL,
  created_by_actor_id TEXT,
  meta_json TEXT
);

-- chunks: derived segments
CREATE TABLE IF NOT EXISTS chunk (
  chunk_id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL,
  workspace_id TEXT NOT NULL,
  start_char INTEGER NOT NULL,
  end_char INTEGER NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (artifact_id) REFERENCES artifact(artifact_id)
);

-- capsules: boundary objects
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
  meta_json TEXT
);

-- edges: lightweight KG
CREATE TABLE IF NOT EXISTS edge (
  edge_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  src_id TEXT NOT NULL,
  dst_id TEXT NOT NULL,
  rel TEXT NOT NULL,      -- depends_on|contradicts|supports|decided_by|blocked_by|defines
  weight REAL NOT NULL DEFAULT 0.5,
  created_at TEXT NOT NULL
);

-- profiles
CREATE TABLE IF NOT EXISTS profile (
  profile_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  owner_actor_id TEXT,
  lens_primary TEXT,
  assumption_signature_json TEXT,
  glossary_exposure_json TEXT,
  stance_refs_json TEXT,
  updated_at TEXT NOT NULL
);

-- exposure ledger
CREATE TABLE IF NOT EXISTS exposure (
  exposure_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  capsule_id TEXT NOT NULL,
  exposure_type TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  strength REAL NOT NULL
);

-- keys for federation (public keys + trust)
CREATE TABLE IF NOT EXISTS trust_key (
  key_id TEXT PRIMARY KEY,
  org_id TEXT,
  label TEXT,
  ed25519_pub_b64 TEXT NOT NULL,
  trust_level TEXT NOT NULL,  -- local|org|consortium
  added_at TEXT NOT NULL
);
```

## 3.2 Full-text search

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS fts_chunks
USING fts5(text, chunk_id UNINDEXED, workspace_id UNINDEXED);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_capsules
USING fts5(title, body, capsule_id UNINDEXED, workspace_id UNINDEXED);
```

## 3.3 Vector storage (pluggable)

* Provide an interface `VectorStore` with backends:

  * `sqlite_vec` backend (preferred)
  * `faiss_sidecar` backend (optional)

You’ll store vectors for:

* chunks
* capsules
* (optional) profile topic centroids

---

# 4) Model layer spec

## 4.1 Model router config (YAML)

```yaml
embedder:
  model: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 64

reranker:
  enabled: false
  model: "cross-encoder/ms-marco-MiniLM-L-6-v2"

llm:
  backend: "llama_cpp"
  models:
    - name: "small"
      path: "/models/qwen2.5-3b-instruct-q4.gguf"
      max_ctx: 4096
    - name: "medium"
      path: "/models/llama-3.1-8b-instruct-q4.gguf"
      max_ctx: 8192

policy:
  typing:
    max_latency_ms: 120
    allow_llm: false
  before_send:
    max_latency_ms: 1200
    allow_llm: true
    llm_tier: "small"
  batch:
    max_latency_ms: 60000
    allow_llm: true
    llm_tier: "medium"
```

## 4.2 Provider interfaces

```python
from typing import Protocol, Iterable

class Embedder(Protocol):
    def embed(self, texts: List[str]) -> List[List[float]]: ...

class Reranker(Protocol):
    def rerank(self, query: str, docs: List[str]) -> List[int]: ...

class LLM(Protocol):
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str: ...
```

---

# 5) Retrieval spec (hybrid)

## 5.1 Retrieval inputs

* query text
* workspace_id
* filters: capsule types, scope, lens_tags, evidence level

## 5.2 Retrieval pipeline

1. FTS top-N (cheap)
2. Vector top-M (semantic)
3. Merge + de-dup
4. Optional rerank (only if policy allows)
5. Return top-K with provenance pointers

---

# 6) Alignment engine spec

## 6.1 Outputs (Alignment Report)

```python
class GapFinding(BaseModel):
    span: Tuple[int, int]                 # char offsets in draft
    kind: str                             # acronym|implicit_prereq|missing_glossary|missing_decision
    description: str
    recipient_actor_id: Optional[str] = None
    suggested_bridge: Optional[str] = None
    supporting_capsule_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

class MismatchFinding(BaseModel):
    span: Tuple[int, int]
    kind: str                             # constraint_conflict|capability_conflict|goal_divergence|evidence_mismatch
    description: str
    conflicting_capsule_id: Optional[str] = None
    recommendation: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)

class RareThoughtFinding(BaseModel):
    span: Tuple[int, int]
    idea_summary: str
    fit_map: List[str] = Field(default_factory=list)   # links to goals/open_questions
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

    context_capsule_ids: List[str] = Field(default_factory=list)   # what was retrieved/used
    policy_decision: str                                           # silent|badge|sidebar|modal
```

## 6.2 Scoring (deterministic, explainable)

### Gap score per span (recipient-aware)

`gap = w1*acronym_unknown + w2*glossary_missing + w3*unseen_dependency + w4*evidence_level_jump`

* `acronym_unknown`: term not expanded and not in recipient glossary exposure
* `unseen_dependency`: referenced decision/constraint not in recipient exposure ledger
* `evidence_level_jump`: statement phrased as “certain” but only hypothesis-level support exists

### Mismatch score

* Hard check: conflict with `Constraint` or `Capability` capsules (keyword + semantic match)
* Soft check: divergence from `Goal` (topic alignment)

### Novelty score (rare thought)

`novelty = 1 - sim(draft_idea_vec, group_centroid_vec)`
`relevance = sim(draft_idea_vec, goal_openq_centroid_vec)`
Flag if `novelty > Tn and relevance > Tr`

## 6.3 Intervention policy

* typing: only show **badge** if blocker_conf > 0.85
* before_send: show **sidebar** if report_value > threshold; **modal** if hard blocker

---

# 7) Rendering engine spec (multi-lens views)

## 7.1 Render request/response

```python
class DraftRenderRequest(BaseModel):
    workspace_id: str
    draft_text: str
    recipients: List[str] = Field(default_factory=list)
    target_lens: Lens
    style: str = "minimal_bridge"  # minimal_bridge|plain_language|exec_summary
    max_added_chars: int = 500

class DraftRenderResponse(BaseModel):
    native: str
    rendered: str
    diff_summary: List[str] = Field(default_factory=list)
    inserted_glossary: List[str] = Field(default_factory=list)
    used_capsule_ids: List[str] = Field(default_factory=list)
```

### Rendering constraints

* Must preserve author voice: only **insert** minimal bridges unless requested.
* Must include “uncertainty framing” for outsiders (evidence level notes).

---

# 8) Debate engine spec (ideas → polarization + seeds)

## 8.1 Idea map output

```python
class IdeaCluster(BaseModel):
    cluster_id: str
    label: str
    capsule_ids: List[str] = Field(default_factory=list)
    chunk_ids: List[str] = Field(default_factory=list)
    centroid_terms: List[str] = Field(default_factory=list)

class StanceAxis(BaseModel):
    axis_id: str
    topic: str
    pole_a_label: str
    pole_b_label: str
    supporting_position_capsules_a: List[str] = Field(default_factory=list)
    supporting_position_capsules_b: List[str] = Field(default_factory=list)

class ContradictionSeed(BaseModel):
    seed_id: str
    claim_a: str
    claim_b: str
    evidence_capsule_ids: List[str] = Field(default_factory=list)
    discriminating_tests: List[str] = Field(default_factory=list)

class IdeaMapResponse(BaseModel):
    workspace_id: str
    query: Optional[str] = None
    clusters: List[IdeaCluster] = Field(default_factory=list)
    stance_axes: List[StanceAxis] = Field(default_factory=list)
    contradiction_seeds: List[ContradictionSeed] = Field(default_factory=list)
    outlier_seeds: List[str] = Field(default_factory=list)   # capsule/chunk ids
```

---

# 9) API spec (FastAPI endpoints)

## 9.1 Auth and tenancy

* v0.1: local token (static) + workspace isolation
* Later: mTLS for multi-host deployments

## 9.2 Endpoints

### Health

* `GET /v1/health` → `{status, version, models_loaded}`

### Ingestion

* `POST /v1/artifact/ingest`

  * body: `{workspace_id, type, title?, body, created_by_actor_id?, meta?}`
  * returns: `{artifact_id, chunks_created, embeddings_created}`

### Capsule lifecycle

* `POST /v1/capsule/propose` (background extraction or user proposal)
* `POST /v1/capsule/publish` (sets scope, redaction, signature)
* `GET /v1/capsule/query?workspace_id=...&type=...&lens=...`

### Draft assist

* `POST /v1/draft/analyze` → `AlignmentReport`
* `POST /v1/draft/render` → `DraftRenderResponse`

### Message explain

* `POST /v1/message/explain` → (same structure as AlignmentReport + sender card)

### Idea map

* `POST /v1/ideas/map` → `IdeaMapResponse`

### Exposure

* `POST /v1/exposure/log` → record what a user has “seen/acked”

---

# 10) Federation spec (optional, decentralized capsules)

## 10.1 What syncs

* Only **published capsules** + edges between published capsules
* No raw artifacts, no chunks by default

## 10.2 Canonicalization + signatures

* Canonical JSON serialization (stable key order)
* `content_hash = sha256(canonical_json_bytes)`
* Signature: Ed25519 over `content_hash`

## 10.3 Wire objects

```python
class CapsuleManifest(BaseModel):
    workspace_id: str
    publisher_org_id: str
    capsules: List[str]                 # capsule_id list
    merkle_root: Optional[str] = None
    generated_at: datetime
    signer_key_id: str
    signature_b64: str
```

```python
class SyncPushRequest(BaseModel):
    workspace_id: str
    from_org_id: str
    manifest: CapsuleManifest
    capsules: List[Capsule] = Field(default_factory=list)   # include only new/updated
    edges: List[Dict[str, Any]] = Field(default_factory=list)
```

```python
class SyncPullRequest(BaseModel):
    workspace_id: str
    known_capsule_ids: List[str] = Field(default_factory=list)
    want_since: Optional[datetime] = None
```

### Merge rules

* Capsules are immutable; updates create a new capsule that `supersedes` old (Decision meta)
* Conflicts produce parallel **Position** capsules (no overwrite)
* Edge set is add-wins (safe union)

### Trust

* Accept only signatures from trusted keys (`trust_key` table)
* Enforce scope: e.g., reject `private` or `org_local` from other orgs

---

# 11) Privacy & redaction spec

## 11.1 Redaction profiles

* `redaction_profile` defines regex and semantic redactions:

  * remove part numbers, vendor names, dimensions, process parameters
* On publish, generate a **shared copy** capsule:

  * `body_shared` replaces sensitive parts with abstract constraints (“tolerance within X”, “material class Y”)

## 11.2 Encryption at rest (pluggable)

Define a `KeyProvider` interface:

* macOS Keychain / Linux secret-service / Windows DPAPI
* Option A: SQLCipher for whole DB
* Option B: app-layer encrypt `artifact.body` only (capsules may remain plaintext for searchability)

(v0.1 can start plaintext + document the hooks.)

---

# 12) Conformance tests (must-have)

### Retrieval

* given a query, top-k must include known relevant capsule in fixture dataset

### Gap detection

* when recipient has not seen glossary term, a gap finding must be produced

### Constraint mismatch

* when draft proposes forbidden policy, mismatch finding references the correct constraint capsule

### Rendering

* rendered text must not exceed `max_added_chars`
* must list used capsules

### Federation

* signature verification passes for trusted keys and fails otherwise
* merge produces union without deleting existing capsules

---

# 13) Milestone implementation plan (A → D)

### Milestone A (2–3 weeks typical)

* SQLite schema + FTS + vector backend interface
* `/artifact/ingest`, chunking + embedding
* `/capsule/query` retrieval (FTS+vector)

### Milestone B

* Glossary capsules + exposure ledger
* `/draft/analyze` fast-pass gap scoring + hard constraint checks

### Milestone C

* Model router + llama.cpp backend
* `/draft/render` multi-lens output (minimal bridge + outsider view)

### Milestone D

* `/message/explain` sender lens card + clarification questions
* Profile updates (assumption signatures, glossary exposure)

(Federation + debate engine are Milestones E/F.)

---

## Appendix A: Minimal request/response examples

### Draft analyze

```json
POST /v1/draft/analyze
{
  "workspace_id": "b6a2...uuid",
  "draft_text": "We can switch to hosted vector DB and get quick wins...",
  "recipients": ["actor_pm_1"],
  "mode": "before_send"
}
```

Response includes blocker:

```json
{
  "blockers": [{
    "kind": "constraint_conflict",
    "description": "Conflicts with 'No cloud services' constraint.",
    "conflicting_capsule_id": "CAP_01H...",
    "confidence": 0.91,
    "span": [13, 33]
  }],
  "policy_decision": "modal"
}
```

---

If you want, I can also provide a **starter FastAPI project skeleton** (files + dependency list + the first endpoints wired to SQLite + embedding) consistent with this spec, so you can begin implementing Milestone A immediately.

---
---
---

Got it — let’s push the spec pack from “v0.1 skeleton” into something you can actually implement as a **multi-service Python daemon** with **clear contracts**, **background workers**, **prompt templates**, **privacy/federation mechanics**, and **integration patterns**.

I’ll call this **SAP Spec Pack v0.2 (Implementation-Ready)**.

---

# SAP Spec Pack v0.2

## 0) Runtime model

You deploy SAP as either:

### Option A — Single local daemon (recommended MVP)

* `sapd` (FastAPI + background workers + SQLite)
* Runs on localhost / Unix domain socket
* Used by any UI client

### Option B — Split services (later)

* `sap-api` (FastAPI)
* `sap-worker` (indexing/extraction)
* `sap-federation` (sync)
* Shared SQLite (or separate stores)

---

# 1) Expanded domain schema

## 1.1 Workspace + Org + Policy

```python
class Workspace(BaseModel):
    workspace_id: str
    name: str
    description: str = ""
    created_at: datetime
    owner_org_id: Optional[str] = None
    default_scope: Scope = Scope.workspace_local
    enabled_lenses: List[Lens] = Field(default_factory=lambda: list(Lens))

class Org(BaseModel):
    org_id: str
    name: str
    domains: List[str] = Field(default_factory=list)  # optional for trust heuristics
    meta: Dict[str, Any] = Field(default_factory=dict)

class PolicyConfig(BaseModel):
    workspace_id: str
    # intervention thresholds
    blocker_conf_modal: float = 0.88
    blocker_conf_badge: float = 0.80
    hint_value_sidebar: float = 0.65

    # privacy rules
    allow_llm_on_typing: bool = False
    allow_llm_before_send: bool = True
    allow_external_sync: bool = False

    # evidence rules (lens-aware expectation defaults)
    expected_evidence_by_lens: Dict[Lens, EvidenceLevel] = Field(default_factory=lambda: {
        Lens.manufacturing: EvidenceLevel.measured,
        Lens.academic: EvidenceLevel.simulated,
        Lens.management: EvidenceLevel.estimate,
        Lens.policy_outsider: EvidenceLevel.estimate,
    })
```

## 1.2 Lens definition object (critical for your scenario)

Lens is not just a label; it’s rules + vocabulary + expectations:

```python
class LensDefinition(BaseModel):
    lens: Lens
    description: str

    # vocabulary mapping and disambiguation
    term_map: Dict[str, str] = Field(default_factory=dict)            # "robustness" -> lens meaning
    synonym_map: Dict[str, List[str]] = Field(default_factory=dict)   # term -> synonyms
    forbidden_jargon: List[str] = Field(default_factory=list)         # outsider lens

    # evidence expectations
    default_evidence_level: EvidenceLevel
    evidence_language: Dict[EvidenceLevel, List[str]] = Field(default_factory=dict)
    # e.g. measured -> ["we measured", "test results", "empirical", "metrology"]

    # what to surface for this lens
    required_sections: List[str] = Field(default_factory=list)
    # outsider: ["purpose", "tradeoffs", "uncertainty", "decision_needed"]
```

Store these as JSON files loaded per workspace (`workspaces/<id>/lens.json`), so companies can customize.

---

# 2) Storage spec v0.2 (tables you’ll actually need)

Add the missing operational pieces:

```sql
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

CREATE TABLE IF NOT EXISTS policy (
  workspace_id TEXT PRIMARY KEY,
  policy_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS redaction_profile (
  redaction_profile_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  name TEXT NOT NULL,
  rules_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

-- job queue (simple local queue to avoid extra infra in MVP)
CREATE TABLE IF NOT EXISTS job (
  job_id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL,
  kind TEXT NOT NULL,            -- ingest|embed|capsule_extract|profile_update|debate_map
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL,          -- queued|running|done|failed
  priority INTEGER NOT NULL DEFAULT 5,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  error TEXT
);
```

This “job table queue” is enough for MVP; later swap for Redis/RQ/Celery without changing API.

---

# 3) Service contracts (API) — concrete and integration-friendly

## 3.1 Transport

* **HTTP over localhost** (default)
* **Unix domain socket** on macOS/Linux (best for local security/perf)
* Optional: WebSocket for streaming typing hints

## 3.2 API objects

### DraftAnalyzeRequest

```python
class DraftAnalyzeRequest(BaseModel):
    workspace_id: str
    draft_text: str
    sender_actor_id: Optional[str] = None
    recipients: List[str] = Field(default_factory=list)
    # if recipient is “role lens” (e.g., steering committee), allow virtual recipients:
    recipient_lenses: List[Lens] = Field(default_factory=list)
    mode: AnalysisMode = AnalysisMode.before_send

    # incremental typing optimization
    draft_id: Optional[str] = None
    changed_spans: Optional[List[Tuple[int,int]]] = None
    max_findings: int = 30
```

### MessageExplainRequest

```python
class MessageExplainRequest(BaseModel):
    workspace_id: str
    message_text: str
    sender_hint: Optional[str] = None          # email/name (optional)
    assumed_sender_actor_id: Optional[str] = None
    recipient_actor_id: Optional[str] = None
    target_lens: Optional[Lens] = None         # if reading as outsider/manager
```

### IdeaMapRequest

```python
class IdeaMapRequest(BaseModel):
    workspace_id: str
    query: Optional[str] = None
    lens: Optional[Lens] = None
    limit_chunks: int = 400
    include_positions: bool = True
```

## 3.3 Endpoint list (v0.2)

**Workspaces / config**

* `POST /v1/workspace/create`
* `GET /v1/workspace/{id}`
* `PUT /v1/workspace/{id}/policy`
* `PUT /v1/workspace/{id}/lens_definitions`

**Ingest**

* `POST /v1/artifact/ingest` (sync returns IDs, queues heavy work)
* `POST /v1/artifact/ingest_batch`

**Capsules**

* `POST /v1/capsule/propose` (manual or AI-assisted)
* `POST /v1/capsule/publish` (sign + redact + scope)
* `GET /v1/capsule/query`
* `POST /v1/capsule/edge/add`

**Alignment**

* `POST /v1/draft/analyze` → `AlignmentReport`
* `POST /v1/draft/render` → multi-lens render response
* `WS /v1/draft/analyze_stream` (optional)

**Explain**

* `POST /v1/message/explain`

**Debate**

* `POST /v1/ideas/map`
* `POST /v1/ideas/summarize_by_lens`

**Exposure**

* `POST /v1/exposure/log`

**Jobs**

* `GET /v1/job/{id}`
* `POST /v1/job/run_next` (worker loop calls this or reads DB directly)

**Federation (optional)**

* `POST /v1/sync/push`
* `POST /v1/sync/pull`
* `POST /v1/trust/add_key`

---

# 4) Alignment engine — deeper algorithm spec

## 4.1 Retrieval bundle (what every analysis starts with)

Return structured context, not just text:

```python
class RetrievedContext(BaseModel):
    goals: List[Capsule] = []
    constraints: List[Capsule] = []
    decisions: List[Capsule] = []
    glossary: List[Capsule] = []
    capabilities: List[Capsule] = []
    positions: List[Capsule] = []
    open_questions: List[Capsule] = []
    evidence: List[Capsule] = []
    raw_hits: List[str] = []  # chunk_ids
```

Retrieval rules:

* Always include **top goals + constraints + latest decisions** even if similarity is mediocre (they’re “guardrails”).
* Then add semantic matches from draft.

## 4.2 Gap detection (recipient + lens aware)

Each draft is split into “claims/spans”:

* acronym spans
* domain terms
* implicit dependencies (decision references, constraint references)
* confidence language cues (“will”, “guaranteed”, “likely”, “hypothesis”)

Gap checks:

1. **Glossary missing for recipient** (term not in recipient exposure)
2. **Decision/constraint unseen** (draft relies on something recipient hasn’t seen)
3. **Lens mismatch** (term has different meaning under recipient lens)
4. **Evidence expectation mismatch** (manufacturing lens expects measured/certified; message is hypothesis-level)

Output action types:

* `bridge_sentence`
* `inline_glossary`
* `link_capsule`
* `ask_clarifying_question`

## 4.3 Mismatch detection (guardrails)

Hard blockers:

* violates `Constraint` capsule
* violates `Capability` bounds (lead time, certification, tolerance, cost class)
* contradicts latest `Decision` (unless marked deliberate divergence)

Soft warnings:

* goal divergence
* evidence mismatch (“this is presented too strongly for current evidence”)
* “school-of-thought collision” (Position A vs Position B)

## 4.4 Rare thought protection

Rare thought pipeline:

* Extract candidate “idea sentences” (claims that propose new approach)
* Compute:

  * novelty vs group centroid
  * relevance to goals/open questions
* If flagged, generate:

  * “fit map”
  * minimal framing options for each lens (manufacturing, academic, management, outsider)
  * suggestion to store as `Position` capsule

---

# 5) Rendering engine — prompt templates (drop-in)

You’ll want **stable prompts** so behavior is predictable.

## 5.1 Prompt: minimal bridge insertion (cross-discipline)

**System**

* “You must preserve the author’s voice and wording. Only insert minimal bridging text.”

**User payload**

* Draft
* Lens target + recipient lens
* Glossary terms definitions
* Relevant constraints/decisions (short)
* Output contract: “Return rendered text + bullet list of insertions (no more than N).”

## 5.2 Prompt: outsider view (policy/manager)

* Must include: purpose, decision needed, tradeoffs, uncertainty, timeline/cost class if available.
* Must avoid jargon; if needed, define in parentheses once.

## 5.3 Prompt: clarifying questions

* Generate 3–7 short questions that reduce ambiguity fastest
* Each question references a specific uncertainty (“Which tolerance range?” “Which validation method?”)

---

# 6) Capsule extraction worker (how your knowledge base grows)

This matters a lot for “academic + industrial + outsider”:

### Worker `capsule_extract`

Input: new artifacts/chunks
Output: proposed capsules (unpublished) of types:

* Goal/Constraint/Decision/Glossary/Capability/Position/OpenQuestion/Evidence

Rules:

* Always store as **proposed** (`is_published=False`)
* UI/client decides what becomes official (publish step)

This prevents “AI creates policy” problems.

---

# 7) Redaction and IP protection spec

## 7.1 Redaction rule DSL (JSON)

```json
{
  "name": "consortium_sanitized",
  "rules": [
    {"type": "regex", "pattern": "\\b[A-Z]{3}-\\d{4}\\b", "replace": "[PART_ID]"},
    {"type": "regex", "pattern": "\\b\\d+(\\.\\d+)?\\s?(mm|um|nm)\\b", "replace": "[DIMENSION]"},
    {"type": "term_map", "terms": {"VendorX": "[SUPPLIER]"}}
  ],
  "semantic_redaction": {
    "enabled": true,
    "instructions": "Remove proprietary parameters; keep abstract constraints and ranges."
  }
}
```

Publish flow:

1. canonicalize capsule JSON
2. apply redaction profile → create a **shared copy** capsule body
3. hash + sign shared copy
4. export only shared copy

---

# 8) Federation protocol (decentralized but controlled)

## 8.1 Sync unit

* Published capsules (sanitized)
* Optional edges between published capsules
* Optional stance maps (“Position capsules”)

## 8.2 Trust

* Ed25519 keys per org/consortium
* Local trust store controls who is accepted
* Scope enforcement: reject foreign `private/org_local`

## 8.3 Merge semantics

* Capsules immutable
* Updates are new capsule versions with `meta.supersedes=[old]`
* Conflicts become parallel `Position` capsules (never overwrite)

---

# 9) Performance & “low consumption” spec

## 9.1 Three latency tiers

* **Typing tier**: <120ms, no LLM, only cached retrieval + heuristic scoring
* **Before-send tier**: <1200ms, allow small LLM only if blocker/gap value high
* **Batch tier**: seconds/minutes, full debate mapping + summarization

## 9.2 Incremental analysis

Use `draft_id` + `changed_spans`:

* only re-embed changed spans (or skip embedding during typing)
* reuse retrieved context for same thread/workspace for a short TTL

## 9.3 Power policy

* If “low power mode”: disable reranker + LLM; only ledger checks + glossary gaps
* If on battery and CPU hot: defer capsule extraction to idle time

---

# 10) Reference implementation scaffolding (what you implement next)

## 10.1 Minimal FastAPI wiring (pattern)

* `sap_api/deps.py` provides:

  * `get_db()`
  * `get_vector_store()`
  * `get_model_router()`
  * `get_policy(workspace_id)`

* endpoints call:

  * `pipelines/ingest.py`
  * `pipelines/draft_analyze.py`
  * `pipelines/message_explain.py`
  * `pipelines/idea_map.py`

## 10.2 Worker loop

A simple worker:

* polls `job` table
* claims job with atomic update
* runs job handler
* updates status

This keeps you infra-free in MVP.

---

# 11) Test fixtures (you’ll want these immediately)

Create a `tests/fixtures/consortium_case/` with:

* 4 actors: manufacturing engineer, academic researcher, PM, outsider/policy
* 10 glossary capsules (terms with lens-specific meanings)
* 3 constraints (no cloud, certification required, budget class)
* 3 decisions (selected approach A, rejected B)
* 2 capability capsules (Org1 manufacturing bounds, Org2 test lab bounds)
* 6 artifacts (emails/chats) that reference jargon + implicit assumptions

Then assert:

* draft to outsider triggers glossary gaps + outsider rendering sections
* academic hypothesis sent to manufacturing triggers evidence mismatch warning
* proposal violating capability bounds triggers blocker referencing correct capsule

---

# 12) Milestones (expanded, actionable task lists)

## Milestone A — “Local RAG substrate”

* SQLite migrations + FTS + vector backend
* ingest + chunk + embed
* capsule query + retrieval bundle

## Milestone B — “Gap + mismatch (no LLM)”

* lens definitions + policy config
* exposure ledger
* gap scoring + hard constraint/capability checks
* draft/analyze endpoint

## Milestone C — “Multi-lens rendering (LLM gated)”

* llama.cpp backend wrapper + router
* prompt templates + safe output parsing
* draft/render endpoint (native/cross/outsider)

## Milestone D — “After-receive explain + profiles”

* message/explain
* profile updates (assumption signatures, glossary exposure)
* clarification question generation

## Milestone E — “Debate engine”

* clustering + stance axes + contradiction seeds
* lens-based summaries

## Milestone F — “Publish + federation”

* redaction profiles
* signing + trust store
* sync push/pull + merge

---

## What I can add next (choose anything, I’ll just do it)

1. **Full OpenAPI schema** (YAML) for these endpoints
2. **Concrete SQLite migration files** + repository skeleton code blocks
3. **Exact prompts** (system/user) for: capsule extraction, rendering, questions
4. **The deterministic scoring functions** (gap/mismatch/novelty) in Python pseudocode ready to paste

Tell me which of the 4 you want first (or say “all”), and I’ll continue directly with the full artifacts.

---
---
---

