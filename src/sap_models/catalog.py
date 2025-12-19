from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class ModelSpec:
    name: str
    kind: str
    tier: str
    local: bool
    max_ctx: int
    latency_ms: int
    memory_gb: float
    cost_per_1k_tokens: float = 0.0
    path: Optional[str] = None


@dataclass
class ModelBudget:
    max_latency_ms: int = 1200
    max_memory_gb: float = 8.0
    allow_remote: bool = False
    max_cost_per_1k_tokens: float = 0.0


class ModelCatalog:
    def __init__(self, specs: Iterable[ModelSpec]):
        self.specs: List[ModelSpec] = list(specs)

    def pick(self, kind: str, tier: str, budget: ModelBudget) -> Optional[ModelSpec]:
        candidates = [s for s in self.specs if s.kind == kind and s.tier == tier]
        if not candidates:
            return None

        filtered = []
        for s in candidates:
            if s.latency_ms > budget.max_latency_ms:
                continue
            if s.memory_gb > budget.max_memory_gb:
                continue
            if not budget.allow_remote and not s.local:
                continue
            if budget.max_cost_per_1k_tokens and s.cost_per_1k_tokens > budget.max_cost_per_1k_tokens:
                continue
            filtered.append(s)

        if not filtered:
            return None
        return sorted(filtered, key=lambda s: (s.latency_ms, s.memory_gb))[0]
