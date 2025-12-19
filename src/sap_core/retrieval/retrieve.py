from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple
import json
import numpy as np

from sap_core.domain.models import Capsule, CapsuleType, EvidenceLevel, Scope


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    return float(np.dot(a, b) / denom)


def fts_capsules(con, workspace_id: str, q: str, limit: int = 30) -> List[str]:
    rows = con.execute(
        "SELECT capsule_id FROM fts_capsules WHERE fts_capsules MATCH ? AND workspace_id=? LIMIT ?",
        (q, workspace_id, limit),
    ).fetchall()
    return [r["capsule_id"] for r in rows]


def load_capsules(con, workspace_id: str, ids: List[str]) -> List[Capsule]:
    if not ids:
        return []
    qmarks = ",".join("?" for _ in ids)
    rows = con.execute(
        f"SELECT * FROM capsule WHERE workspace_id=? AND capsule_id IN ({qmarks})",
        [workspace_id, *ids],
    ).fetchall()

    out: List[Capsule] = []
    for r in rows:
        out.append(
            Capsule(
                capsule_id=r["capsule_id"],
                workspace_id=r["workspace_id"],
                type=CapsuleType(r["type"]),
                title=r["title"],
                body=r["body"],
                lens_tags=json.loads(r["lens_tags_json"] or "[]"),
                scope=Scope(r["scope"]),
                evidence_level=EvidenceLevel(r["evidence_level"]),
                confidence=float(r["confidence"]),
                created_at=datetime.fromisoformat(r["created_at"]),
                created_by_actor_id=r["created_by_actor_id"],
                provenance=json.loads(r["provenance_json"] or "{}"),
                is_published=bool(r["is_published"]),
                redaction_profile_id=r["redaction_profile_id"],
                content_hash=r["content_hash"],
                signer_key_id=r["signer_key_id"],
                signature_b64=r["signature_b64"],
                meta=json.loads(r["meta_json"] or "{}"),
            )
        )
    return out


def vector_top_capsules(
    con,
    workspace_id: str,
    query_vec: List[float],
    limit: int = 50,
) -> List[Tuple[str, float]]:
    rows = con.execute(
        "SELECT owner_id, vec_json FROM embedding WHERE workspace_id=? AND owner_type='capsule'",
        (workspace_id,),
    ).fetchall()
    if not rows:
        return []
    qv = np.array(query_vec, dtype=np.float32)
    scored: List[Tuple[str, float]] = []
    for r in rows:
        v = np.array(json.loads(r["vec_json"]), dtype=np.float32)
        scored.append((r["owner_id"], _cos(qv, v)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def retrieve_bundle(
    con,
    workspace_id: str,
    query: str,
    query_vec: Optional[List[float]] = None,
    limit: int = 40,
) -> List[Capsule]:
    guard = con.execute(
        "SELECT capsule_id FROM capsule WHERE workspace_id=? AND type IN ('goal','constraint','decision') ORDER BY created_at DESC LIMIT 30",
        (workspace_id,),
    ).fetchall()
    guard_ids = [r["capsule_id"] for r in guard]

    ids = set(guard_ids)

    if query.strip():
        for cid in fts_capsules(con, workspace_id, query, limit=30):
            ids.add(cid)

    if query_vec is not None:
        for cid, _score in vector_top_capsules(con, workspace_id, query_vec, limit=limit):
            ids.add(cid)

    return load_capsules(con, workspace_id, list(ids))
