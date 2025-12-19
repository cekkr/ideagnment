from __future__ import annotations

CAPSULE_EXTRACT_SYSTEM = """You extract boundary-object capsules from project text.
Rules:
- Do NOT invent facts. Use only what is in INPUT.
- Output JSON only, matching the schema.
- Propose capsules; do not mark them as published.
- Preserve dissent: if conflicting viewpoints exist, create Position capsules, not fixes.
"""

CAPSULE_EXTRACT_USER = """<INPUT>
{text}
</INPUT>

Extract candidate capsules relevant to cross-organization collaboration:
- Goal, Constraint, Decision, Glossary, Capability, Assumption, Evidence, Position, OpenQuestion
For each capsule:
- title: short
- body: 1-5 sentences
- lens_tags: subset of [manufacturing, academic, management, policy_outsider]
- evidence_level: one of [hypothesis, estimate, simulated, measured, certified]
- confidence: 0..1
- meta: include structured fields when obvious (e.g., Capability: lead_time_days, certifications)

Return JSON:
{
  "capsules": [
    {
      "type": "goal|constraint|decision|glossary|capability|assumption|evidence|position|open_question",
      "title": "...",
      "body": "...",
      "lens_tags": ["..."],
      "evidence_level": "...",
      "confidence": 0.0,
      "meta": {}
    }
  ]
}
"""

RENDER_MIN_BRIDGE_SYSTEM = """You revise text by inserting minimal bridging context.
Rules:
- Preserve the author's voice. Keep original sentences whenever possible.
- Only add short insertions (1-2 sentences) where needed.
- If you define a term, do it once (parentheses or a short clause).
- Do not remove dissent. If the draft challenges constraints, keep it but add an explicit exception framing.
Output must be JSON only.
"""

RENDER_MIN_BRIDGE_USER = """Target lens: {target_lens}
Max added characters: {max_added_chars}

Known glossary (term -> definition):
{glossary_block}

Guardrails:
Goals:
{goals_block}

Constraints:
{constraints_block}

Decisions:
{decisions_block}

Draft:
<INPUT>
{draft}
</INPUT>

Return JSON:
{
  "rendered": "...",
  "diff_summary": ["..."],
  "inserted_glossary": ["..."],
  "used_capsule_ids": ["..."]
}
"""

RENDER_OUTSIDER_SYSTEM = """You produce an outsider/manager/policy-friendly version of a message.
Rules:
- No jargon unless defined once.
- Must include: Purpose, Decision Needed, Options/Tradeoffs, Uncertainty/Evidence level, Next Steps.
- Do NOT claim certainty beyond input evidence.
Output JSON only.
"""

RENDER_OUTSIDER_USER = """Max added characters: {max_added_chars}

Project guardrails (goals/constraints/decisions) in brief:
{guardrails_block}

Draft:
<INPUT>
{draft}
</INPUT>

Return JSON:
{
  "rendered": "...",
  "diff_summary": ["..."],
  "inserted_glossary": ["..."],
  "used_capsule_ids": ["..."]
}
"""

CLARIFY_QUESTIONS_SYSTEM = """You generate clarification questions that reduce ambiguity fastest.
Rules:
- 3 to 7 questions.
- Each question must be short and actionable.
- Prefer questions that clarify: evidence level, constraints, timeline, capability bounds, definitions.
Output JSON only.
"""

CLARIFY_QUESTIONS_USER = """Message:
<INPUT>
{text}
</INPUT>

Known constraints/capabilities:
{guardrails_block}

Return JSON:
{
  "questions": ["..."]
}
"""
