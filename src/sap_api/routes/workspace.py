from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
import ulid

from sap_api.deps import get_con
from sap_core.domain.models import Workspace, WorkspaceCreateRequest

router = APIRouter(prefix="/v1/workspace", tags=["workspace"])


@router.post("/create", response_model=Workspace)
def create_workspace(req: WorkspaceCreateRequest, con=Depends(get_con)) -> Workspace:
    workspace_id = str(ulid.new())
    now = datetime.utcnow().isoformat()

    con.execute(
        """
        INSERT INTO workspace(workspace_id, name, description, created_at, owner_org_id, default_scope)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            req.name,
            req.description,
            now,
            req.owner_org_id,
            req.default_scope.value,
        ),
    )

    return Workspace(
        workspace_id=workspace_id,
        name=req.name,
        description=req.description,
        created_at=datetime.fromisoformat(now),
        owner_org_id=req.owner_org_id,
        default_scope=req.default_scope,
    )


@router.get("/{workspace_id}", response_model=Workspace)
def get_workspace(workspace_id: str, con=Depends(get_con)) -> Workspace:
    row = con.execute(
        "SELECT * FROM workspace WHERE workspace_id=?",
        (workspace_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="workspace not found")

    return Workspace(
        workspace_id=row["workspace_id"],
        name=row["name"],
        description=row["description"] or "",
        created_at=datetime.fromisoformat(row["created_at"]),
        owner_org_id=row["owner_org_id"],
        default_scope=row["default_scope"],
    )
