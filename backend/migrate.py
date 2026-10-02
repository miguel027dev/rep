import hashlib
import json
import os
from pathlib import Path

from psycopg.types.json import Jsonb

from .db import get_db
from .logging_utils import logger

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "migrations"
LOCK_ID = 842_260_101


def _legacy_to_normalized(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.tyvon_accounts') AS legacy")
        if not cur.fetchone()["legacy"]:
            return
        cur.execute("SELECT a.user_id, a.state, u.email FROM tyvon_accounts a JOIN tyvon_users u ON u.id=a.user_id")
        rows = cur.fetchall()
    if not rows:
        return
    from .account import persist_state
    for row in rows:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM tyvon_profiles WHERE user_id=%s", (row["user_id"],))
            if cur.fetchone():
                continue
        state = row["state"]
        if isinstance(state, str):
            try:
                state = json.loads(state)
            except json.JSONDecodeError:
                continue
        if isinstance(state, dict):
            persist_state(conn, row["user_id"], row["email"], state, expected_revision=None, migration_mode=True)


def _cleanup(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tyvon_sessions WHERE expires_at <= (EXTRACT(EPOCH FROM NOW())*1000)::BIGINT")
        cur.execute("DELETE FROM tyvon_oauth WHERE expires_at <= (EXTRACT(EPOCH FROM NOW())*1000)::BIGINT")
        cur.execute("DELETE FROM tyvon_auth_limits WHERE expires_at <= (EXTRACT(EPOCH FROM NOW())*1000)::BIGINT")
        cur.execute("DELETE FROM tyvon_email_tokens WHERE expires_at <= (EXTRACT(EPOCH FROM NOW())*1000)::BIGINT")
        cur.execute("DELETE FROM tyvon_ai_limits WHERE day_bucket < FLOOR(EXTRACT(EPOCH FROM NOW())/86400)-2")


def run_migrations():
    if not os.getenv("DATABASE_URL"):
        return
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (LOCK_ID,))
        try:
            cur.execute("""
              CREATE TABLE IF NOT EXISTS tyvon_schema_migrations (
                name TEXT PRIMARY KEY,
                checksum TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
              )
            """)
            for path in sorted(MIGRATIONS.glob("*.sql")):
                sql = path.read_text(encoding="utf-8")
                checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
                cur.execute("SELECT checksum FROM tyvon_schema_migrations WHERE name=%s", (path.name,))
                row = cur.fetchone()
                if row:
                    if row["checksum"] != checksum:
                        logger.warning("migration checksum changed: %s", path.name)
                    continue
                cur.execute(sql)
                cur.execute("INSERT INTO tyvon_schema_migrations(name,checksum) VALUES(%s,%s)", (path.name, checksum))
            conn.commit()
            _legacy_to_normalized(conn)
            _cleanup(conn)
            conn.commit()
        finally:
            cur.execute("SELECT pg_advisory_unlock(%s)", (LOCK_ID,))
            conn.commit()


if __name__ == "__main__":
    run_migrations()
