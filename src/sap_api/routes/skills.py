from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

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


@router.post("/report", response_model=SkillRecord)
def report(req: SkillReportRequest, con=Depends(get_con)) -> SkillRecord:
    try:
        return report_skill(con, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/earn", response_model=SkillRecord)
def earn(req: SkillEarnRequest, con=Depends(get_con)) -> SkillRecord:
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
    con=Depends(get_con),
) -> List[SkillRecord]:
    try:
        return query_skills(con, workspace_id, actor_id, claim_type, view)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
