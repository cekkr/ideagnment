from __future__ import annotations

from dataclasses import dataclass

from sap_core.domain.models import AnalysisMode


@dataclass
class RouteDecision:
    allow_llm: bool
    llm_tier: str = "small"
    max_tokens: int = 280
    temperature: float = 0.2


class ModelRouter:
    def __init__(self, allow_llm_on_typing: bool, allow_llm_before_send: bool):
        self.allow_llm_on_typing = allow_llm_on_typing
        self.allow_llm_before_send = allow_llm_before_send

    def route(self, mode: AnalysisMode, value_score: float) -> RouteDecision:
        if mode == AnalysisMode.typing:
            return RouteDecision(
                allow_llm=self.allow_llm_on_typing and value_score > 0.85,
                llm_tier="small",
                max_tokens=160,
            )
        if mode == AnalysisMode.before_send:
            return RouteDecision(
                allow_llm=self.allow_llm_before_send and value_score > 0.55,
                llm_tier="small",
                max_tokens=320,
            )
        if mode == AnalysisMode.batch:
            return RouteDecision(allow_llm=True, llm_tier="medium", max_tokens=700, temperature=0.15)
        return RouteDecision(allow_llm=False)
