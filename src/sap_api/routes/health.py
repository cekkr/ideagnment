from __future__ import annotations

from fastapi import APIRouter

from sap_core.domain.models import HealthResponse

router = APIRouter(prefix="/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.2")
