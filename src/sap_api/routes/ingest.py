from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from sap_api.deps import get_con
from sap_core.domain.models import ArtifactIngestRequest, ArtifactIngestResponse
from sap_core.pipelines.ingest import ingest_artifact

router = APIRouter(prefix="/v1/artifact", tags=["ingest"])


@router.post("/ingest", response_model=ArtifactIngestResponse)
def ingest(req: ArtifactIngestRequest, con=Depends(get_con)) -> ArtifactIngestResponse:
    try:
        return ingest_artifact(con, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
