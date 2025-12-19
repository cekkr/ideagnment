from __future__ import annotations

from typing import List, Optional
import json

from fastapi import APIRouter, Depends, Header, HTTPException

from sap_api.deps import get_con
from sap_core.domain.models import (
    SkillClaimType,
    SkillEarnRequest,
    SkillRecord,
    SkillReportRequest,
    SkillView,
)
from sap_core.pipelines.skills import earn_skill, query_skills, report_skill

router = APIRouter(prefix="/v1/skills", tags=["skills"])

_INSTITUTION_ROLES = {"org_admin", "org_delegate", "org_representative", "manager"}


def _load_actor(con, actor_id: str, workspace_id: Optional[str]) -> dict:
    row = con.execute(
        "SELECT actor_id, org_id, roles_json, workspace_id FROM actor WHERE actor_id=?",
        (actor_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="actor not found")
    if workspace_id and row["workspace_id"] != workspace_id:
        raise HTTPException(status_code=403, detail="actor not in workspace")
    roles = json.loads(row["roles_json"] or "[]")
    return {"actor_id": row["actor_id"], "org_id": row["org_id"], "roles": roles}


def _require_institution_access(auth_actor: dict, org_id: Optional[str]) -> None:
    if not org_id:
        raise HTTPException(status_code=403, detail="org_id required for institution view")
    if auth_actor.get("org_id") != org_id:
        raise HTTPException(status_code=403, detail="actor not in requested org")
    if not any(role in _INSTITUTION_ROLES for role in auth_actor.get("roles", [])):
        raise HTTPException(status_code=403, detail="insufficient role for institution view")


@router.post("/report", response_model=SkillRecord)
def report(
    req: SkillReportRequest,
    x_actor_id: str = Header(..., alias="X-Actor-Id"),
    x_org_id: Optional[str] = Header(None, alias="X-Org-Id"),
    con=Depends(get_con),
) -> SkillRecord:
    auth_actor = _load_actor(con, x_actor_id, req.workspace_id)
    if req.actor_id != x_actor_id:
        _require_institution_access(auth_actor, x_org_id)
        target_actor = _load_actor(con, req.actor_id, req.workspace_id)
        if target_actor.get("org_id") != x_org_id:
            raise HTTPException(status_code=403, detail="target actor not in org")
    try:
        return report_skill(con, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/earn", response_model=SkillRecord)
def earn(
    req: SkillEarnRequest,
    x_actor_id: str = Header(..., alias="X-Actor-Id"),
    x_org_id: Optional[str] = Header(None, alias="X-Org-Id"),
    con=Depends(get_con),
) -> SkillRecord:
    auth_actor = _load_actor(con, x_actor_id, req.workspace_id)
    if req.actor_id != x_actor_id:
        _require_institution_access(auth_actor, x_org_id)
        target_actor = _load_actor(con, req.actor_id, req.workspace_id)
        if target_actor.get("org_id") != x_org_id:
            raise HTTPException(status_code=403, detail="target actor not in org")
    try:
        return earn_skill(con, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/query", response_model=List[SkillRecord])
def query(
    workspace_id: str,
    actor_id: Optional[str] = None,
    claim_type: Optional[SkillClaimType] = None,
    view: SkillView = SkillView.person,
    x_actor_id: str = Header(..., alias="X-Actor-Id"),
    x_org_id: Optional[str] = Header(None, alias="X-Org-Id"),
    con=Depends(get_con),
) -> List[SkillRecord]:
    auth_actor = _load_actor(con, x_actor_id, workspace_id)
    org_filter = None
    if view == SkillView.person:
        if actor_id is not None and actor_id != x_actor_id:
            raise HTTPException(status_code=403, detail="person view limited to self")
        actor_id = x_actor_id
    else:
        _require_institution_access(auth_actor, x_org_id)
        org_filter = x_org_id
        if actor_id is not None:
            target_actor = _load_actor(con, actor_id, workspace_id)
            if target_actor.get("org_id") != x_org_id:
                raise HTTPException(status_code=403, detail="target actor not in org")
    try:
        return query_skills(con, workspace_id, actor_id, claim_type, view, org_filter)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
