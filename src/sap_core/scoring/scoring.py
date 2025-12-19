from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import re

import numpy as np

from sap_core.domain.models import (
    Capsule,
    CapsuleType,
    EvidenceLevel,
    GapFinding,
    MismatchFinding,
    RareThoughtFinding,
)


_ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{2,}\b")
_CONFIDENT_WORDS = re.compile(r"\b(must|will|guarantee|always|never|cannot fail)\b", re.IGNORECASE)
_HEDGE_WORDS = re.compile(r"\b(might|may|could|suggests|hypothesis|likely|uncertain)\b", re.IGNORECASE)

EVID_ORDER: Dict[EvidenceLevel, int] = {
    EvidenceLevel.hypothesis: 0,
    EvidenceLevel.estimate: 1,
    EvidenceLevel.simulated: 2,
    EvidenceLevel.measured: 3,
    EvidenceLevel.certified: 4,
}


def evidence_word_level(text: str) -> EvidenceLevel:
    if _CONFIDENT_WORDS.search(text):
        return EvidenceLevel.measured
    if _HEDGE_WORDS.search(text):
        return EvidenceLevel.hypothesis
    return EvidenceLevel.estimate


def split_spans(text: str) -> List[Tuple[int, int]]:
    spans = []
    start = 0
    for m in re.finditer(r"[.!?]\s+", text):
        end = m.end()
        spans.append((start, end))
        start = end
    if start < len(text):
        spans.append((start, len(text)))
    return spans


def extract_acronyms(text: str) -> List[Tuple[str, Tuple[int, int]]]:
    out = []
    for m in _ACRONYM_RE.finditer(text):
        out.append((m.group(0), (m.start(), m.end())))
    return out


def build_glossary_index(capsules: List[Capsule]) -> Dict[str, str]:
    idx: Dict[str, str] = {}
    for c in capsules:
        if c.type != CapsuleType.glossary:
            continue
        if "terms" in c.meta and isinstance(c.meta["terms"], list):
            for t in c.meta["terms"]:
                term = (t.get("term") or "").strip()
                definition = (t.get("definition") or "").strip()
                if term and definition:
                    idx[term.lower()] = definition
        else:
            parts = c.body.split(":", 1)
            if len(parts) == 2:
                idx[parts[0].strip().lower()] = parts[1].strip()
    return idx


def gap_findings(
    draft: str,
    glossary_idx: Dict[str, str],
    recipient_exposure_terms: Optional[Dict[str, float]] = None,
    recipient_actor_id: Optional[str] = None,
) -> List[GapFinding]:
    recipient_exposure_terms = recipient_exposure_terms or {}

    gaps: List[GapFinding] = []

    for acr, span in extract_acronyms(draft):
        known = recipient_exposure_terms.get(acr.lower(), 0.0) > 0.5 or (acr.lower() in glossary_idx)
        if not known:
            gaps.append(
                GapFinding(
                    span=span,
                    kind="acronym_unknown",
                    description=f"Acronym '{acr}' likely unknown to recipient.",
                    recipient_actor_id=recipient_actor_id,
                    suggested_bridge=f"{acr} = [define once here].",
                    supporting_capsule_ids=[],
                    confidence=0.75,
                )
            )

    for term, definition in glossary_idx.items():
        if term in draft.lower():
            seen = recipient_exposure_terms.get(term, 0.0) > 0.5
            if not seen:
                pos = draft.lower().find(term)
                span = (pos, pos + len(term))
                gaps.append(
                    GapFinding(
                        span=span,
                        kind="missing_glossary",
                        description=(
                            f"Term '{term}' used; recipient likely hasn't seen its project-specific definition."
                        ),
                        recipient_actor_id=recipient_actor_id,
                        suggested_bridge=f"{term} ({definition})",
                        supporting_capsule_ids=[],
                        confidence=0.65,
                    )
                )

    return gaps


def mismatch_findings(
    draft: str,
    constraints: List[Capsule],
    capabilities: List[Capsule],
    expected_evidence: Optional[EvidenceLevel],
) -> List[MismatchFinding]:
    mismatches: List[MismatchFinding] = []

    if expected_evidence is not None:
        stated = evidence_word_level(draft)
        if EVID_ORDER[stated] < EVID_ORDER[expected_evidence]:
            mismatches.append(
                MismatchFinding(
                    span=(0, min(len(draft), 120)),
                    kind="evidence_mismatch",
                    description=(
                        f"Draft reads as '{stated.value}' but audience expects at least '{expected_evidence.value}'."
                    ),
                    conflicting_capsule_id=None,
                    recommendation="Add uncertainty framing or attach evidence/measurement plan.",
                    confidence=0.72,
                )
            )

    lower = draft.lower()
    for c in constraints:
        key = c.title.lower()
        if any(w in lower for w in key.split() if len(w) >= 5):
            if "no cloud" in c.title.lower() and ("cloud" in lower or "hosted" in lower):
                mismatches.append(
                    MismatchFinding(
                        span=(0, min(len(draft), 200)),
                        kind="constraint_conflict",
                        description=f"Potential conflict with constraint: {c.title}",
                        conflicting_capsule_id=c.capsule_id,
                        recommendation=(
                            "Reframe as local-first alternative or request an exception explicitly."
                        ),
                        confidence=0.88,
                    )
                )

    for cap in capabilities:
        meta = cap.meta or {}
        if "lead_time_days" in meta and ("next week" in lower or "tomorrow" in lower):
            mismatches.append(
                MismatchFinding(
                    span=(0, min(len(draft), 200)),
                    kind="capability_conflict",
                    description=(
                        "Timeline wording may conflict with capability lead time "
                        f"({meta.get('lead_time_days')} days): {cap.title}"
                    ),
                    conflicting_capsule_id=cap.capsule_id,
                    recommendation=(
                        "State an achievable schedule or split prototype vs certified production plan."
                    ),
                    confidence=0.70,
                )
            )

    return mismatches


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    return float(np.dot(a, b) / denom)


def rare_thought_findings(
    idea_spans: List[Tuple[int, int]],
    idea_vecs: List[List[float]],
    group_centroid_vec: Optional[List[float]],
    goal_centroid_vec: Optional[List[float]],
    draft: str,
) -> List[RareThoughtFinding]:
    if group_centroid_vec is None or goal_centroid_vec is None:
        return []
    g = np.array(group_centroid_vec, dtype=np.float32)
    t = np.array(goal_centroid_vec, dtype=np.float32)

    out: List[RareThoughtFinding] = []
    for (span, vec) in zip(idea_spans, idea_vecs):
        v = np.array(vec, dtype=np.float32)
        novelty = max(0.0, min(1.0, 1.0 - cosine(v, g)))
        relevance = max(0.0, min(1.0, cosine(v, t)))

        if novelty > 0.55 and relevance > 0.40:
            snippet = draft[span[0]:span[1]].strip()
            out.append(
                RareThoughtFinding(
                    span=span,
                    idea_summary=(snippet[:200] + ("..." if len(snippet) > 200 else "")),
                    fit_map=["Relates to current goals/open questions (high semantic overlap)."],
                    protect_notes=(
                        "Novel viewpoint detected: frame it as a testable option; do not dilute into consensus."
                    ),
                    novelty=novelty,
                    relevance=relevance,
                )
            )

    return out
