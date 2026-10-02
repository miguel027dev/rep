import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


class DatabaseUnavailable(RuntimeError):
    pass


def database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise DatabaseUnavailable("DATABASE_URL não configurada")
    return url


@contextmanager
def get_db():
    try:
        conn = psycopg.connect(database_url(), row_factory=dict_row, connect_timeout=8)
    except (psycopg.Error, OSError) as exc:
        raise DatabaseUnavailable("Banco indisponível") from exc
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ping_db():
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 AS ok")
        return cur.fetchone()["ok"] == 1
