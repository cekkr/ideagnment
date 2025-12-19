from __future__ import annotations

from fastapi import FastAPI

from sap_store.sqlite.migrate import apply_all
from sap_api.routes.health import router as health_router
from sap_api.routes.workspace import router as workspace_router
from sap_api.routes.ingest import router as ingest_router
from sap_api.routes.capsule import router as capsule_router
from sap_api.routes.draft import router as draft_router


def create_app() -> FastAPI:
    apply_all()
    app = FastAPI(title="SAP", version="0.2")
    app.include_router(health_router)
    app.include_router(workspace_router)
    app.include_router(ingest_router)
    app.include_router(capsule_router)
    app.include_router(draft_router)
    return app


app = create_app()
