from __future__ import annotations

from typing import Dict, Optional

from sap_models.catalog import ModelSpec
from sap_models.llm import LocalLLM


class ModelRegistry:
    def __init__(self) -> None:
        self._llms: Dict[str, LocalLLM] = {}

    def get_llm(self, spec: ModelSpec) -> Optional[LocalLLM]:
        if spec.path is None:
            return None
        if spec.name in self._llms:
            return self._llms[spec.name]
        llm = LocalLLM(spec.path, n_ctx=spec.max_ctx)
        self._llms[spec.name] = llm
        return llm


registry = ModelRegistry()
