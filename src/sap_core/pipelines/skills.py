from __future__ import annotations

from datetime import datetime
import json
from typing import List, Optional

import ulid

from sap_core.domain.models import (
    Scope,
    SkillClaimType,
    SkillEarnRequest,
    SkillEvidence,
    SkillRecord,
    SkillReportRequest,
    SkillView,
)
from sap_core.privacy.partitioning import filter_skill_records


def _ensure_workspace(con, workspace_id: str) -> None:
    row = con.execute(
        "SELECT workspace_id FROM workspace WHERE workspace_id=?",
        (workspace_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"workspace_id not found: {workspace_id}")


def _ensure_actor(con, actor_id: str) -> None:
    row = con.execute(
        "SELECT actor_id FROM actor WHERE actor_id=?",
        (actor_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"actor_id not found: {actor_id}")


def _serialize_evidence(evidence: Optional[SkillEvidence]) -> str:
    if evidence is None:
        return "{}"
    return json.dumps(evidence.model_dump())


def report_skill(con, req: SkillReportRequest) -> SkillRecord:
    _ensure_workspace(con, req.workspace_id)
    _ensure_actor(con, req.actor_id)

    skill_id = str(ulid.new())
    now = datetime.utcnow().isoformat()
    evidence = SkillEvidence(notes=req.notes) if req.notes else None

    con.execute(
        """
        INSERT INTO skill(
            skill_id, workspace_id, actor_id, skill_name, claim_type, level, confidence, visibility,
            evidence_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            skill_id,
            req.workspace_id,
            req.actor_id,
            req.skill_name,
            SkillClaimType.reported.value,
            req.level,
            req.confidence,
            req.visibility.value,
            _serialize_evidence(evidence),
            now,
            now,
        ),
    )

    return SkillRecord(
        skill_id=skill_id,
        workspace_id=req.workspace_id,
        actor_id=req.actor_id,
        skill_name=req.skill_name,
        claim_type=SkillClaimType.reported,
        level=req.level,
        confidence=req.confidence,
        visibility=req.visibility,
        evidence=evidence,
        created_at=datetime.fromisoformat(now),
        updated_at=datetime.fromisoformat(now),
    )


def earn_skill(con, req: SkillEarnRequest) -> SkillRecord:
    _ensure_workspace(con, req.workspace_id)
    _ensure_actor(con, req.actor_id)

    skill_id = str(ulid.new())
    now = datetime.utcnow().isoformat()
    evidence = SkillEvidence(
        capsule_ids=req.evidence_capsule_ids,
        artifact_ids=req.evidence_artifact_ids,
        notes=req.notes,
    )

    con.execute(
        """
        INSERT INTO skill(
            skill_id, workspace_id, actor_id, skill_name, claim_type, level, confidence, visibility,
            evidence_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            skill_id,
            req.workspace_id,
            req.actor_id,
            req.skill_name,
            SkillClaimType.earned.value,
            req.level,
            req.confidence,
            req.visibility.value,
            _serialize_evidence(evidence),
            now,
            now,
        ),
    )

    return SkillRecord(
        skill_id=skill_id,
        workspace_id=req.workspace_id,
        actor_id=req.actor_id,
        skill_name=req.skill_name,
        claim_type=SkillClaimType.earned,
        level=req.level,
        confidence=req.confidence,
        visibility=req.visibility,
        evidence=evidence,
        created_at=datetime.fromisoformat(now),
        updated_at=datetime.fromisoformat(now),
    )


def query_skills(
    con,
    workspace_id: str,
    actor_id: Optional[str],
    claim_type: Optional[SkillClaimType],
    view: SkillView,
) -> List[SkillRecord]:
    _ensure_workspace(con, workspace_id)

    sql = "SELECT * FROM skill WHERE workspace_id=?"
    params: List[object] = [workspace_id]

    if actor_id:
        sql += " AND actor_id=?"
        params.append(actor_id)
    if claim_type:
        sql += " AND claim_type=?"
        params.append(claim_type.value)

    sql += " ORDER BY updated_at DESC"
    rows = con.execute(sql, params).fetchall()

    records: List[SkillRecord] = []
    for r in rows:
        evidence = json.loads(r["evidence_json"] or "{}")
        record = SkillRecord(
            skill_id=r["skill_id"],
            workspace_id=r["workspace_id"],
            actor_id=r["actor_id"],
            skill_name=r["skill_name"],
            claim_type=SkillClaimType(r["claim_type"]),
            level=r["level"],
            confidence=float(r["confidence"]),
            visibility=Scope(r["visibility"]),
            evidence=SkillEvidence(**evidence) if evidence else None,
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
        )
        records.append(record)

    return filter_skill_records(records, view=view)
