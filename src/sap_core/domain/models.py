from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

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


class WorkspaceCreateRequest(BaseModel):
    name: str
    description: str = ""
    owner_org_id: Optional[str] = None
    default_scope: Scope = Scope.workspace_local


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


class ArtifactIngestRequest(BaseModel):
    workspace_id: str
    type: ArtifactType
    title: Optional[str] = None
    body: str
    created_by_actor_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class ArtifactIngestResponse(BaseModel):
    artifact_id: str
    chunks_created: int
    embeddings_created: int


class DraftAnalyzeRequest(BaseModel):
    workspace_id: str
    draft_text: str
    recipients: List[str] = Field(default_factory=list)
    recipient_lenses: List[Lens] = Field(default_factory=list)
    mode: AnalysisMode = AnalysisMode.before_send


class DraftRenderRequest(BaseModel):
    workspace_id: str
    draft_text: str
    target_lens: Lens
    max_added_chars: int = 500


class DraftRenderResponse(BaseModel):
    native: str
    rendered: str
    diff_summary: List[str] = Field(default_factory=list)
    inserted_glossary: List[str] = Field(default_factory=list)
    used_capsule_ids: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: Optional[List[str]] = None
