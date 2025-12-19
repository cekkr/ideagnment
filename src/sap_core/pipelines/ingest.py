from __future__ import annotations

from datetime import datetime
import json
from typing import Iterable, List, Tuple

import ulid

from sap_core.domain.models import ArtifactIngestRequest, ArtifactIngestResponse


def _chunk_text(text: str, max_len: int = 1000, overlap: int = 150) -> List[Tuple[int, int, str]]:
    if max_len <= 0:
        return []
    chunks: List[Tuple[int, int, str]] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(text_len, start + max_len)
        chunk = text[start:end]
        chunks.append((start, end, chunk))
        if end == text_len:
            break
        start = max(0, end - overlap)
    return chunks


def _ensure_workspace(con, workspace_id: str) -> None:
    row = con.execute(
        "SELECT workspace_id FROM workspace WHERE workspace_id=?",
        (workspace_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"workspace_id not found: {workspace_id}")


def ingest_artifact(con, req: ArtifactIngestRequest) -> ArtifactIngestResponse:
    _ensure_workspace(con, req.workspace_id)

    now = datetime.utcnow().isoformat()
    artifact_id = str(ulid.new())

    con.execute(
        """
        INSERT INTO artifact(
            artifact_id, workspace_id, type, title, body, created_at, created_by_actor_id, meta_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            artifact_id,
            req.workspace_id,
            req.type.value,
            req.title,
            req.body,
            now,
            req.created_by_actor_id,
            json.dumps(req.meta or {}),
        ),
    )

    chunks = _chunk_text(req.body)
    for start, end, text in chunks:
        chunk_id = str(ulid.new())
        con.execute(
            """
            INSERT INTO chunk(chunk_id, artifact_id, workspace_id, start_char, end_char, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (chunk_id, artifact_id, req.workspace_id, start, end, text, now),
        )
        con.execute(
            "INSERT INTO fts_chunks(text, chunk_id, workspace_id) VALUES (?, ?, ?)",
            (text, chunk_id, req.workspace_id),
        )

    return ArtifactIngestResponse(
        artifact_id=artifact_id,
        chunks_created=len(chunks),
        embeddings_created=0,
    )
