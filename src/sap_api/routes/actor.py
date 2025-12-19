from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
import ulid

from sap_api.deps import get_con
from sap_core.domain.models import Actor, ActorCreateRequest

router = APIRouter(prefix="/v1/actor", tags=["actor"])


@router.post("/create", response_model=Actor)
def create_actor(req: ActorCreateRequest, con=Depends(get_con)) -> Actor:
    row = con.execute(
        "SELECT workspace_id FROM workspace WHERE workspace_id=?",
        (req.workspace_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="workspace not found")

    actor_id = str(ulid.new())

    con.execute(
        """
        INSERT INTO actor(actor_id, workspace_id, display_name, org_id, roles_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            actor_id,
            req.workspace_id,
            req.display_name,
            req.org_id,
            json.dumps(req.roles),
        ),
    )

    return Actor(
        actor_id=actor_id,
        workspace_id=req.workspace_id,
        display_name=req.display_name,
        org_id=req.org_id,
        roles=req.roles,
    )


@router.get("/{actor_id}", response_model=Actor)
def get_actor(actor_id: str, con=Depends(get_con)) -> Actor:
    row = con.execute("SELECT * FROM actor WHERE actor_id=?", (actor_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="actor not found")

    roles = json.loads(row["roles_json"] or "[]")

    return Actor(
        actor_id=row["actor_id"],
        workspace_id=row["workspace_id"],
        display_name=row["display_name"],
        org_id=row["org_id"],
        roles=roles,
    )
