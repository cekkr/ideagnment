from __future__ import annotations

from datetime import datetime
import json


def claim_next_job(con):
    row = con.execute(
        """
        SELECT job_id, kind, payload_json
        FROM job
        WHERE status='queued'
        ORDER BY priority ASC, created_at ASC
        LIMIT 1
        """,
    ).fetchone()
    if row is None:
        return None

    con.execute(
        "UPDATE job SET status='running', updated_at=? WHERE job_id=?",
        (datetime.utcnow().isoformat(), row["job_id"]),
    )
    return {
        "job_id": row["job_id"],
        "kind": row["kind"],
        "payload": json.loads(row["payload_json"]),
    }


def run_once(con) -> bool:
    job = claim_next_job(con)
    if job is None:
        return False

    # TODO: dispatch by job kind.
    con.execute(
        "UPDATE job SET status='done', updated_at=? WHERE job_id=?",
        (datetime.utcnow().isoformat(), job["job_id"]),
    )
    return True
