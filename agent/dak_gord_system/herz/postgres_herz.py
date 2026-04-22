from __future__ import annotations

import atexit
import os
from contextlib import contextmanager

from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

_pool: ConnectionPool | None = None


def _hole_db_uri() -> str:
    uri = os.getenv("DAK_GORD_DB_URI")
    if not uri:
        raise RuntimeError(
            "Umgebungsvariable DAK_GORD_DB_URI nicht gesetzt. "
            "Beispiel: export DAK_GORD_DB_URI='postgresql://user:pass@host/db'"
        )
    return uri


def hole_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(conninfo=_hole_db_uri(), min_size=1, max_size=5)
    return _pool


def schliesse_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


atexit.register(schliesse_pool)


@contextmanager
def postgres_kontext():
    yield PostgresSaver(hole_pool())
