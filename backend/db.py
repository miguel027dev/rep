import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


def database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL não configurada")
    return url


@contextmanager
def get_db():
    conn = psycopg.connect(database_url(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    schema = """
    DO $tyvon_migration$
    BEGIN
      IF to_regclass('public.rep_users') IS NOT NULL AND to_regclass('public.tyvon_users') IS NULL THEN ALTER TABLE public.rep_users RENAME TO tyvon_users; END IF;
      IF to_regclass('public.rep_sessions') IS NOT NULL AND to_regclass('public.tyvon_sessions') IS NULL THEN ALTER TABLE public.rep_sessions RENAME TO tyvon_sessions; END IF;
      IF to_regclass('public.rep_oauth') IS NOT NULL AND to_regclass('public.tyvon_oauth') IS NULL THEN ALTER TABLE public.rep_oauth RENAME TO tyvon_oauth; END IF;
      IF to_regclass('public.rep_auth_limits') IS NOT NULL AND to_regclass('public.tyvon_auth_limits') IS NULL THEN ALTER TABLE public.rep_auth_limits RENAME TO tyvon_auth_limits; END IF;
      IF to_regclass('public.rep_accounts') IS NOT NULL AND to_regclass('public.tyvon_accounts') IS NULL THEN ALTER TABLE public.rep_accounts RENAME TO tyvon_accounts; END IF;
      IF to_regclass('public.rep_privacy_requests') IS NOT NULL AND to_regclass('public.tyvon_privacy_requests') IS NULL THEN ALTER TABLE public.rep_privacy_requests RENAME TO tyvon_privacy_requests; END IF;
      IF to_regclass('public.rep_social_activity') IS NOT NULL AND to_regclass('public.tyvon_social_activity') IS NULL THEN ALTER TABLE public.rep_social_activity RENAME TO tyvon_social_activity; END IF;
      IF to_regclass('public.rep_user_email_provider') IS NOT NULL AND to_regclass('public.tyvon_user_email_provider') IS NULL THEN ALTER INDEX public.rep_user_email_provider RENAME TO tyvon_user_email_provider; END IF;
      IF to_regclass('public.rep_sessions_user_id') IS NOT NULL AND to_regclass('public.tyvon_sessions_user_id') IS NULL THEN ALTER INDEX public.rep_sessions_user_id RENAME TO tyvon_sessions_user_id; END IF;
      IF to_regclass('public.rep_sessions_expires_at') IS NOT NULL AND to_regclass('public.tyvon_sessions_expires_at') IS NULL THEN ALTER INDEX public.rep_sessions_expires_at RENAME TO tyvon_sessions_expires_at; END IF;
      IF to_regclass('public.rep_privacy_requests_email_created') IS NOT NULL AND to_regclass('public.tyvon_privacy_requests_email_created') IS NULL THEN ALTER INDEX public.rep_privacy_requests_email_created RENAME TO tyvon_privacy_requests_email_created; END IF;
      IF to_regclass('public.rep_social_activity_created') IS NOT NULL AND to_regclass('public.tyvon_social_activity_created') IS NULL THEN ALTER INDEX public.rep_social_activity_created RENAME TO tyvon_social_activity_created; END IF;
      IF to_regclass('public.rep_social_activity_user_created') IS NOT NULL AND to_regclass('public.tyvon_social_activity_user_created') IS NULL THEN ALTER INDEX public.rep_social_activity_user_created RENAME TO tyvon_social_activity_user_created; END IF;
    END
    $tyvon_migration$;

    CREATE TABLE IF NOT EXISTS tyvon_users (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL,
      name TEXT NOT NULL DEFAULT '',
      provider TEXT NOT NULL,
      google_sub TEXT UNIQUE,
      password_hash TEXT,
      salt TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS tyvon_user_email_provider
      ON tyvon_users (email, provider);

    CREATE TABLE IF NOT EXISTS tyvon_sessions (
      token_hash TEXT PRIMARY KEY,
      user_id TEXT NOT NULL REFERENCES tyvon_users(id) ON DELETE CASCADE,
      expires_at BIGINT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS tyvon_sessions_user_id ON tyvon_sessions(user_id);
    CREATE INDEX IF NOT EXISTS tyvon_sessions_expires_at ON tyvon_sessions(expires_at);

    CREATE TABLE IF NOT EXISTS tyvon_oauth (
      state_hash TEXT PRIMARY KEY,
      verifier TEXT NOT NULL,
      expires_at BIGINT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tyvon_auth_limits (
      id TEXT PRIMARY KEY,
      attempts INTEGER NOT NULL,
      expires_at BIGINT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tyvon_accounts (
      user_id TEXT PRIMARY KEY,
      state JSONB NOT NULL,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS tyvon_privacy_requests (
      id TEXT PRIMARY KEY,
      user_id TEXT REFERENCES tyvon_users(id) ON DELETE SET NULL,
      email TEXT NOT NULL,
      kind TEXT NOT NULL,
      details TEXT NOT NULL DEFAULT '',
      status TEXT NOT NULL DEFAULT 'received',
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS tyvon_privacy_requests_email_created
      ON tyvon_privacy_requests (email, created_at DESC);

    CREATE TABLE IF NOT EXISTS tyvon_social_activity (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL REFERENCES tyvon_users(id) ON DELETE CASCADE,
      display_name TEXT NOT NULL,
      workout_name TEXT NOT NULL,
      sets INTEGER NOT NULL,
      minutes INTEGER NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE INDEX IF NOT EXISTS tyvon_social_activity_created
      ON tyvon_social_activity(created_at DESC);
    CREATE INDEX IF NOT EXISTS tyvon_social_activity_user_created
      ON tyvon_social_activity(user_id, created_at DESC);
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
