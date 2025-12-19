from __future__ import annotations

from sap_store.sqlite.db import db_session
from sap_models.config import load_model_config
from sap_models.router import ModelRouter


def get_con():
    with db_session() as con:
        yield con


def get_model_router() -> ModelRouter:
    cfg = load_model_config()
    return ModelRouter(
        allow_llm_on_typing=False,
        allow_llm_before_send=True,
        catalog=cfg.catalog,
        budget=cfg.budget,
    )
