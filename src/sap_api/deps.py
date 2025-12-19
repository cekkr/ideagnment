from __future__ import annotations

from sap_store.sqlite.db import db_session


def get_con():
    with db_session() as con:
        yield con
