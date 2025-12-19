from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from sap_models.catalog import ModelBudget, ModelCatalog, ModelSpec


DEFAULT_CONFIG_PATH = Path("config") / "models.json"


@dataclass
class ModelConfig:
    catalog: ModelCatalog
    budget: ModelBudget
    specs_by_name: Dict[str, ModelSpec]


class ModelConfigLoader:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_CONFIG_PATH
        self._cached: Optional[ModelConfig] = None
        self._cached_mtime: Optional[float] = None

    def load(self) -> ModelConfig:
        if not self.path.exists():
            return self._fallback()

        mtime = self.path.stat().st_mtime
        if self._cached and self._cached_mtime == mtime:
            return self._cached

        data = json.loads(self.path.read_text(encoding="utf-8"))
        models = [ModelSpec(**m) for m in data.get("models", [])]
        budget = ModelBudget(**data.get("budget", {}))
        catalog = ModelCatalog(models)
        specs_by_name = {m.name: m for m in models}

        cfg = ModelConfig(catalog=catalog, budget=budget, specs_by_name=specs_by_name)
        self._cached = cfg
        self._cached_mtime = mtime
        return cfg

    def _fallback(self) -> ModelConfig:
        budget = ModelBudget(max_latency_ms=1200, max_memory_gb=8.0, allow_remote=False)
        catalog = ModelCatalog([])
        return ModelConfig(catalog=catalog, budget=budget, specs_by_name={})


_loader = ModelConfigLoader(Path(os.environ.get("SAP_MODEL_CATALOG_PATH", DEFAULT_CONFIG_PATH)))


def load_model_config() -> ModelConfig:
    return _loader.load()
