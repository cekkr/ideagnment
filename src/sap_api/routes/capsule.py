from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends

from sap_api.deps import get_con
from sap_core.domain.models import Capsule, CapsuleType, Lens, Scope
from sap_core.retrieval.retrieve import fts_capsules, load_capsules

router = APIRouter(prefix="/v1/capsule", tags=["capsule"])


@router.get("/query", response_model=List[Capsule])
def query_capsules(
    workspace_id: str,
    type: Optional[CapsuleType] = None,
    lens: Optional[Lens] = None,
    scope: Optional[Scope] = None,
    q: Optional[str] = None,
    limit: int = 50,
    con=Depends(get_con),
) -> List[Capsule]:
    ids: List[str] = []
    if q:
        ids = fts_capsules(con, workspace_id, q, limit=limit)
    else:
        sql = "SELECT capsule_id FROM capsule WHERE workspace_id=?"
        params: List[object] = [workspace_id]
        if type is not None:
            sql += " AND type=?"
            params.append(type.value)
        if scope is not None:
            sql += " AND scope=?"
            params.append(scope.value)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = con.execute(sql, params).fetchall()
        ids = [r["capsule_id"] for r in rows]

    capsules = load_capsules(con, workspace_id, ids)
    if lens is not None:
        capsules = [c for c in capsules if lens in c.lens_tags]
    return capsules
