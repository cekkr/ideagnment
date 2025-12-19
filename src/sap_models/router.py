from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sap_core.domain.models import AnalysisMode
from sap_models.catalog import ModelBudget, ModelCatalog


@dataclass
class RouteDecision:
    allow_llm: bool
    llm_tier: str = "small"
    max_tokens: int = 280
    temperature: float = 0.2
    model_name: Optional[str] = None


class ModelRouter:
    def __init__(
        self,
        allow_llm_on_typing: bool,
        allow_llm_before_send: bool,
        catalog: Optional[ModelCatalog] = None,
        budget: Optional[ModelBudget] = None,
    ):
        self.allow_llm_on_typing = allow_llm_on_typing
        self.allow_llm_before_send = allow_llm_before_send
        self.catalog = catalog
        self.budget = budget

    def route(self, mode: AnalysisMode, value_score: float) -> RouteDecision:
        decision = RouteDecision(allow_llm=False)
        if mode == AnalysisMode.typing:
            decision = RouteDecision(
                allow_llm=self.allow_llm_on_typing and value_score > 0.85,
                llm_tier="small",
                max_tokens=160,
            )
        elif mode == AnalysisMode.before_send:
            decision = RouteDecision(
                allow_llm=self.allow_llm_before_send and value_score > 0.55,
                llm_tier="small",
                max_tokens=320,
            )
        elif mode == AnalysisMode.batch:
            decision = RouteDecision(
                allow_llm=True,
                llm_tier="medium",
                max_tokens=700,
                temperature=0.15,
            )

        if decision.allow_llm and self.catalog and self.budget:
            spec = self.catalog.pick("llm", decision.llm_tier, self.budget)
            if spec is not None:
                decision.model_name = spec.name
        return decision
