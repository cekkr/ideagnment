from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .db import DEFAULT_DB_PATH, db_session

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def ensure_migrations_table(con) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          filename TEXT NOT NULL UNIQUE,
          applied_at TEXT NOT NULL
        );
        """
    )


def applied(con) -> set[str]:
    rows = con.execute("SELECT filename FROM schema_migrations").fetchall()
    return {r["filename"] for r in rows}


def apply_all(db_path: Path = DEFAULT_DB_PATH) -> None:
    with db_session(db_path) as con:
        ensure_migrations_table(con)
        done = applied(con)
        files = sorted(p for p in MIGRATIONS_DIR.glob("*.sql"))
        for f in files:
            if f.name in done:
                continue
            sql = f.read_text(encoding="utf-8")
            con.executescript(sql)
            con.execute(
                "INSERT INTO schema_migrations(filename, applied_at) VALUES(?, ?)",
                (f.name, datetime.utcnow().isoformat()),
            )
