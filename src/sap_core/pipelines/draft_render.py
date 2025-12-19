from __future__ import annotations

from typing import List
import json

from sap_core.domain.models import CapsuleType, Lens
from sap_core.prompts.templates import (
    RENDER_MIN_BRIDGE_SYSTEM,
    RENDER_MIN_BRIDGE_USER,
    RENDER_OUTSIDER_SYSTEM,
    RENDER_OUTSIDER_USER,
)


def _block(title: str, items: List[str]) -> str:
    if not items:
        return f"{title}: (none)"
    return f"{title}:\n- " + "\n- ".join(items)


def render_draft(
    llm,
    draft: str,
    capsules,
    target_lens: Lens,
    max_added_chars: int = 500,
):
    goals = [c for c in capsules if c.type == CapsuleType.goal]
    constraints = [c for c in capsules if c.type == CapsuleType.constraint]
    decisions = [c for c in capsules if c.type == CapsuleType.decision]
    glossary = [c for c in capsules if c.type == CapsuleType.glossary]

    glossary_block = "\n".join([f"- {g.title}: {g.body}" for g in glossary][:20])
    used_ids = [c.capsule_id for c in (goals + constraints + decisions + glossary)]

    if llm is None:
        extra = ""
        if target_lens == Lens.policy_outsider:
            extra = "\n\n[Purpose]\n...\n[Decision Needed]\n...\n[Tradeoffs]\n...\n[Uncertainty]\n..."
        return {
            "native": draft,
            "rendered": draft + extra,
            "diff_summary": ["LLM unavailable; returned template-only rendering."],
            "inserted_glossary": [],
            "used_capsule_ids": used_ids,
        }

    if target_lens == Lens.policy_outsider:
        guardrails_block = (
            _block("Goals", [g.title for g in goals])
            + "\n"
            + _block("Constraints", [c.title for c in constraints])
            + "\n"
            + _block("Decisions", [d.title for d in decisions])
        )
        prompt = RENDER_OUTSIDER_SYSTEM + "\n\n" + RENDER_OUTSIDER_USER.format(
            max_added_chars=max_added_chars,
            guardrails_block=guardrails_block,
            draft=draft,
        )
    else:
        prompt = RENDER_MIN_BRIDGE_SYSTEM + "\n\n" + RENDER_MIN_BRIDGE_USER.format(
            target_lens=target_lens.value,
            max_added_chars=max_added_chars,
            glossary_block=glossary_block,
            goals_block=_block("Goals", [g.title for g in goals]),
            constraints_block=_block("Constraints", [c.title for c in constraints]),
            decisions_block=_block("Decisions", [d.title for d in decisions]),
            draft=draft,
        )

    raw = llm.generate(prompt, max_tokens=420, temperature=0.2)
    data = json.loads(raw)
    data["native"] = draft
    if "used_capsule_ids" not in data:
        data["used_capsule_ids"] = used_ids
    return data
