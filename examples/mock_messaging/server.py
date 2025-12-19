from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DEMO_DIR = Path(__file__).resolve().parent
ROOT_DIR = DEMO_DIR.parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

DEMO_DB_PATH = DEMO_DIR / "demo.db"
os.environ.setdefault("SAP_DB_PATH", str(DEMO_DB_PATH))

import ulid
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse

from sap_api.app import create_app
from sap_api.deps import get_con
from sap_core.domain.models import (
    ArtifactIngestRequest,
    ArtifactType,
    Lens,
    Scope,
    SkillEarnRequest,
    SkillReportRequest,
)
from sap_core.pipelines.ingest import ingest_artifact
from sap_core.pipelines.skills import earn_skill, report_skill
from sap_store.sqlite.db import db_session

DEMO_STATE: Dict[str, Any] = {}

CIRCLE_CONFIG = [
    {
        "circle_id": "product-core",
        "name": "Product Core",
        "role": "facilitator",
        "member_keys": ["lina", "aya", "omar"],
        "tags": ["Vision: automation with empathy", "Priority: onboarding"],
    },
    {
        "circle_id": "research-loop",
        "name": "Research Loop",
        "role": "contributor",
        "member_keys": ["lina", "aya"],
        "tags": ["Lens: field interviews"],
    },
    {
        "circle_id": "ops-alliance",
        "name": "Ops Alliance",
        "role": "observer",
        "member_keys": ["omar"],
        "tags": ["Constraint: legal review"],
    },
]

LEDGER_EVENTS = [
    {
        "label": "Circle vision shift: prioritize guided automation",
        "date": "2024-02",
        "circle_id": "product-core",
    },
    {
        "label": "Constraint added: compliance review before pilot",
        "date": "2024-04",
        "circle_id": "ops-alliance",
    },
    {
        "label": "Skill delta: customer research depth +1",
        "date": "2024-05",
        "circle_id": "research-loop",
    },
]

DEMO_DRAFT = (
    "Hi team, I drafted a co-pilot framing for the automation rollout. I also propose a "
    "90-day human review window and tracking a trust gap metric so Ops can see quality guardrails. "
    "If we need cloud support, we can keep data local and stage the hosted pilot later. "
    "Can we align on which stories should be highlighted to reflect the empathy principle?"
)


def _ensure_workspace(con, name: str, description: str, owner_org_id: Optional[str]) -> str:
    row = con.execute("SELECT workspace_id FROM workspace WHERE name=?", (name,)).fetchone()
    if row:
        return row["workspace_id"]

    workspace_id = str(ulid.new())
    now = datetime.utcnow().isoformat()
    con.execute(
        """
        INSERT INTO workspace(workspace_id, name, description, created_at, owner_org_id, default_scope)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            name,
            description,
            now,
            owner_org_id,
            Scope.workspace_local.value,
        ),
    )
    return workspace_id


def _ensure_actor(con, workspace_id: str, display_name: str, org_id: Optional[str], roles: List[str]) -> str:
    row = con.execute(
        "SELECT actor_id FROM actor WHERE workspace_id=? AND display_name=?",
        (workspace_id, display_name),
    ).fetchone()
    if row:
        return row["actor_id"]

    actor_id = str(ulid.new())
    con.execute(
        """
        INSERT INTO actor(actor_id, workspace_id, display_name, org_id, roles_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (actor_id, workspace_id, display_name, org_id, json.dumps(roles)),
    )
    return actor_id


def _ensure_capsule(
    con,
    workspace_id: str,
    capsule_type: str,
    title: str,
    body: str,
    actor_id: str,
    meta: Optional[Dict[str, Any]] = None,
) -> str:
    row = con.execute(
        "SELECT capsule_id FROM capsule WHERE workspace_id=? AND type=? AND title=?",
        (workspace_id, capsule_type, title),
    ).fetchone()
    if row:
        capsule_id = row["capsule_id"]
    else:
        capsule_id = str(ulid.new())
        now = datetime.utcnow().isoformat()
        con.execute(
            """
            INSERT INTO capsule(
                capsule_id, workspace_id, type, title, body, lens_tags_json, scope,
                evidence_level, confidence, created_at, created_by_actor_id, provenance_json,
                is_published, redaction_profile_id, content_hash, signer_key_id, signature_b64, meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                capsule_id,
                workspace_id,
                capsule_type,
                title,
                body,
                json.dumps(["management"]),
                Scope.workspace_local.value,
                "estimate",
                0.82,
                now,
                actor_id,
                json.dumps({}),
                0,
                None,
                None,
                None,
                None,
                json.dumps(meta or {}),
            ),
        )

    row = con.execute(
        "SELECT 1 FROM fts_capsules WHERE capsule_id=?",
        (capsule_id,),
    ).fetchone()
    if not row:
        con.execute(
            "INSERT INTO fts_capsules(title, body, capsule_id, workspace_id) VALUES (?, ?, ?, ?)",
            (title, body, capsule_id, workspace_id),
        )
    return capsule_id


def _ensure_exposure(con, workspace_id: str, actor_id: str, capsule_id: str) -> None:
    row = con.execute(
        "SELECT exposure_id FROM exposure WHERE workspace_id=? AND actor_id=? AND capsule_id=?",
        (workspace_id, actor_id, capsule_id),
    ).fetchone()
    if row:
        return
    con.execute(
        """
        INSERT INTO exposure(exposure_id, workspace_id, actor_id, capsule_id, exposure_type, timestamp, strength)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(ulid.new()),
            workspace_id,
            actor_id,
            capsule_id,
            "seen",
            datetime.utcnow().isoformat(),
            0.85,
        ),
    )


def _ensure_skill_report(con, req: SkillReportRequest) -> None:
    row = con.execute(
        """
        SELECT skill_id FROM skill
        WHERE workspace_id=? AND actor_id=? AND skill_name=? AND claim_type='reported'
        """,
        (req.workspace_id, req.actor_id, req.skill_name),
    ).fetchone()
    if row:
        return
    report_skill(con, req)


def _ensure_skill_earn(con, req: SkillEarnRequest) -> None:
    row = con.execute(
        """
        SELECT skill_id FROM skill
        WHERE workspace_id=? AND actor_id=? AND skill_name=? AND claim_type='earned'
        """,
        (req.workspace_id, req.actor_id, req.skill_name),
    ).fetchone()
    if row:
        return
    earn_skill(con, req)


def _ensure_artifact(
    con,
    workspace_id: str,
    title: str,
    body: str,
    actor_id: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    row = con.execute(
        "SELECT artifact_id FROM artifact WHERE workspace_id=? AND title=?",
        (workspace_id, title),
    ).fetchone()
    if row:
        return

    ingest_artifact(
        con,
        ArtifactIngestRequest(
            workspace_id=workspace_id,
            type=ArtifactType.chat,
            title=title,
            body=body,
            created_by_actor_id=actor_id,
            meta=meta or {},
        ),
    )


def _list_messages(con, workspace_id: str) -> List[Dict[str, Any]]:
    rows = con.execute(
        """
        SELECT a.display_name AS author_name, art.*
        FROM artifact art
        LEFT JOIN actor a ON a.actor_id = art.created_by_actor_id
        WHERE art.workspace_id=?
        ORDER BY art.created_at ASC
        """,
        (workspace_id,),
    ).fetchall()

    messages: List[Dict[str, Any]] = []
    for r in rows:
        meta = json.loads(r["meta_json"] or "{}")
        messages.append(
            {
                "artifact_id": r["artifact_id"],
                "author": r["author_name"] or "Unknown",
                "circle_id": meta.get("circle_id"),
                "timestamp": r["created_at"],
                "body": r["body"],
                "chips": meta.get("context_chips", []),
            }
        )
    return messages


def seed_demo_data() -> Dict[str, Any]:
    with db_session() as con:
        workspace_id = _ensure_workspace(
            con,
            name="CircleMail Demo",
            description="Mock messaging demo for alignment workflows.",
            owner_org_id="harbor-studio",
        )

        actor_ids = {
            "lina": _ensure_actor(
                con,
                workspace_id,
                display_name="Lina Patel",
                org_id="harbor-studio",
                roles=["facilitator"],
            ),
            "aya": _ensure_actor(
                con,
                workspace_id,
                display_name="Aya Lin",
                org_id="harbor-studio",
                roles=["member"],
            ),
            "omar": _ensure_actor(
                con,
                workspace_id,
                display_name="Omar Jones",
                org_id="harbor-studio",
                roles=["ops_delegate"],
            ),
        }

        capsule_ids = {
            "goal": _ensure_capsule(
                con,
                workspace_id,
                "goal",
                "Reduce onboarding to 3 days",
                "Move new accounts from kickoff to first value in 3 days.",
                actor_ids["lina"],
            ),
            "decision": _ensure_capsule(
                con,
                workspace_id,
                "decision",
                "Pilot automation with 2 teams in Q3",
                "Pilot the co-pilot workflow with two teams before full rollout.",
                actor_ids["lina"],
            ),
            "constraint": _ensure_capsule(
                con,
                workspace_id,
                "constraint",
                "No cloud-based automation during pilot",
                "Keep pilot workflows local-first for compliance review.",
                actor_ids["lina"],
            ),
            "capability": _ensure_capsule(
                con,
                workspace_id,
                "capability",
                "Compliance review lead time",
                "Ops review requires a minimum of 10 days.",
                actor_ids["omar"],
                meta={"lead_time_days": 10},
            ),
            "glossary_copilot": _ensure_capsule(
                con,
                workspace_id,
                "glossary",
                "co-pilot",
                "co-pilot: automation that augments human judgment.",
                actor_ids["lina"],
                meta={
                    "terms": [
                        {"term": "co-pilot", "definition": "automation that augments human judgment"}
                    ]
                },
            ),
            "glossary_trust": _ensure_capsule(
                con,
                workspace_id,
                "glossary",
                "trust gap",
                "trust gap: distance between measured and perceived reliability.",
                actor_ids["lina"],
                meta={
                    "terms": [
                        {
                            "term": "trust gap",
                            "definition": "distance between measured and perceived reliability",
                        }
                    ]
                },
            ),
        }

        _ensure_exposure(con, workspace_id, actor_ids["aya"], capsule_ids["glossary_copilot"])

        _ensure_skill_report(
            con,
            SkillReportRequest(
                workspace_id=workspace_id,
                actor_id=actor_ids["lina"],
                skill_name="alignment facilitation",
                level=0.7,
                confidence=0.86,
                visibility=Scope.workspace_local,
                notes="Peer validated during Q1 vision syncs.",
            ),
        )
        _ensure_skill_earn(
            con,
            SkillEarnRequest(
                workspace_id=workspace_id,
                actor_id=actor_ids["aya"],
                skill_name="customer research depth",
                level=0.6,
                confidence=0.8,
                visibility=Scope.workspace_local,
                notes="Validated in 3 recent field interviews.",
            ),
        )

        _ensure_artifact(
            con,
            workspace_id,
            title="Onboarding automation Q3: kickoff notes",
            body=(
                "We should frame the automation layer as a co-pilot, not a handoff. "
                "Ops are worried about losing the feedback loop during the pilot."
            ),
            actor_id=actor_ids["aya"],
            meta={
                "circle_id": "product-core",
                "context_chips": [
                    "Implicit: feedback loop is a quality gate",
                    "Vision: empathy in automation",
                ],
            },
        )
        _ensure_artifact(
            con,
            workspace_id,
            title="Onboarding automation Q3: draft response",
            body=(
                "Agree. I can draft a version that clarifies we keep human review for the first "
                "90 days and measure the trust gap."
            ),
            actor_id=actor_ids["lina"],
            meta={
                "circle_id": "product-core",
                "context_chips": [
                    "Constraint: 90-day review window",
                    "Metric: trust gap",
                ],
            },
        )

    circle_state = []
    for circle in CIRCLE_CONFIG:
        members = [actor_ids[key] for key in circle["member_keys"]]
        circle_state.append(
            {
                "circle_id": circle["circle_id"],
                "name": circle["name"],
                "role": circle["role"],
                "member_ids": members,
                "member_count": len(members),
                "tags": circle["tags"],
            }
        )

    return {
        "workspace": {
            "workspace_id": workspace_id,
            "name": "CircleMail Demo",
            "description": "Mock messaging demo for alignment workflows.",
        },
        "actor": {
            "actor_id": actor_ids["lina"],
            "display_name": "Lina Patel",
            "org_id": "harbor-studio",
        },
        "actors": [
            {
                "actor_id": actor_ids["lina"],
                "display_name": "Lina Patel",
                "org_id": "harbor-studio",
            },
            {
                "actor_id": actor_ids["aya"],
                "display_name": "Aya Lin",
                "org_id": "harbor-studio",
            },
            {
                "actor_id": actor_ids["omar"],
                "display_name": "Omar Jones",
                "org_id": "harbor-studio",
            },
        ],
        "recipients": [
            {
                "actor_id": actor_ids["aya"],
                "display_name": "Aya Lin",
                "lens": Lens.management.value,
            }
        ],
        "circles": circle_state,
        "ledger": LEDGER_EVENTS,
        "thread": {
            "title": "Onboarding automation Q3",
            "participants": 6,
            "last_update_minutes": 40,
            "tags": [
                "Goal: reduce onboarding to 3 days",
                "Decision: pilot automation with 2 teams",
            ],
        },
        "draft": DEMO_DRAFT,
        "context": {
            "glossary": ["co-pilot", "trust gap", "empathy loop"],
            "open_questions": ["Who owns escalation?"],
            "exposure": "Ops Alliance has seen draft v2",
            "capsules": ["Goals", "Constraints", "Decisions"],
        },
    }


app: FastAPI = create_app()


@app.on_event("startup")
def _startup_seed() -> None:
    global DEMO_STATE
    if not DEMO_STATE:
        DEMO_STATE = seed_demo_data()


@app.get("/")
def root() -> FileResponse:
    return FileResponse(DEMO_DIR / "index.html")


@app.get("/demo/state")
def demo_state() -> Dict[str, Any]:
    if not DEMO_STATE:
        DEMO_STATE.update(seed_demo_data())
    return DEMO_STATE


@app.get("/demo/messages")
def demo_messages(con=Depends(get_con)) -> Dict[str, Any]:
    if not DEMO_STATE:
        DEMO_STATE.update(seed_demo_data())
    workspace_id = DEMO_STATE.get("workspace", {}).get("workspace_id")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="demo state not initialized")
    return {"messages": _list_messages(con, workspace_id)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8788, reload=False)
