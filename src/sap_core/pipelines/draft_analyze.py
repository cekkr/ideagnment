from __future__ import annotations

from typing import Dict, List, Optional
import json

from sap_core.domain.models import (
    AlignmentReport,
    AnalysisMode,
    CapsuleType,
    GapFinding,
    Lens,
    PolicyConfig,
)
from sap_core.retrieval.retrieve import retrieve_bundle
from sap_core.scoring.scoring import build_glossary_index, gap_findings, mismatch_findings


def load_policy(con, workspace_id: str) -> PolicyConfig:
    row = con.execute("SELECT policy_json FROM policy WHERE workspace_id=?", (workspace_id,)).fetchone()
    if not row:
        return PolicyConfig(workspace_id=workspace_id)
    return PolicyConfig(**json.loads(row["policy_json"]))


def recipient_term_exposure(con, workspace_id: str, actor_id: str) -> Dict[str, float]:
    rows = con.execute(
        """
        SELECT c.body, c.meta_json
        FROM exposure e
        JOIN capsule c ON c.capsule_id = e.capsule_id
        WHERE e.workspace_id=? AND e.actor_id=? AND c.type='glossary'
        """,
        (workspace_id, actor_id),
    ).fetchall()
    out: Dict[str, float] = {}
    for r in rows:
        meta = json.loads(r["meta_json"] or "{}")
        if "terms" in meta:
            for t in meta["terms"]:
                term = (t.get("term") or "").strip().lower()
                if term:
                    out[term] = max(out.get(term, 0.0), 0.8)
        else:
            body = r["body"]
            parts = body.split(":", 1)
            if parts:
                key = parts[0].strip().lower()
                out[key] = max(out.get(key, 0.0), 0.8)
    return out


def decide_policy(report: AlignmentReport, policy: PolicyConfig) -> str:
    max_block = max((b.confidence for b in report.blockers), default=0.0)
    value = max(max_block, 0.4 * len(report.clarity_gaps) / 10.0 + 0.3 * len(report.rare_thoughts) / 10.0)

    if max_block >= policy.blocker_conf_modal:
        return "modal"
    if max_block >= policy.blocker_conf_badge:
        return "badge"
    if value >= policy.hint_value_sidebar:
        return "sidebar"
    return "silent"


def analyze_draft(
    con,
    workspace_id: str,
    draft_text: str,
    recipients: List[str],
    recipient_lenses: List[Lens],
    mode: AnalysisMode,
    query_vec: Optional[List[float]] = None,
) -> AlignmentReport:
    policy = load_policy(con, workspace_id)
    capsules = retrieve_bundle(con, workspace_id, query=draft_text[:600], query_vec=query_vec)

    constraints = [c for c in capsules if c.type == CapsuleType.constraint]
    capabilities = [c for c in capsules if c.type == CapsuleType.capability]
    glossary_caps = [c for c in capsules if c.type == CapsuleType.glossary]
    glossary_idx = build_glossary_index(glossary_caps)

    expected = None
    if recipient_lenses:
        levels = [policy.expected_evidence_by_lens.get(l) for l in recipient_lenses]
        levels = [x for x in levels if x is not None]
        if levels:
            order = {
                "hypothesis": 0,
                "estimate": 1,
                "simulated": 2,
                "measured": 3,
                "certified": 4,
            }
            expected = max(levels, key=lambda e: order[e.value])

    all_gaps: List[GapFinding] = []
    for rid in recipients:
        exposure_terms = recipient_term_exposure(con, workspace_id, rid)
        all_gaps.extend(gap_findings(draft_text, glossary_idx, exposure_terms, recipient_actor_id=rid))

    blockers = mismatch_findings(draft_text, constraints, capabilities, expected)

    report = AlignmentReport(
        mode=mode,
        workspace_id=workspace_id,
        recipients=recipients,
        lens_target=recipient_lenses[0] if recipient_lenses else None,
        blockers=blockers,
        clarity_gaps=all_gaps,
        rare_thoughts=[],
        context_capsule_ids=[c.capsule_id for c in capsules],
        policy_decision="silent",
    )
    report.policy_decision = decide_policy(report, policy)
    return report
