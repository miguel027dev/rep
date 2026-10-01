CREATE TABLE IF NOT EXISTS rep_users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL,
  name TEXT NOT NULL DEFAULT '',
  provider TEXT NOT NULL,
  google_sub TEXT UNIQUE,
  password_hash TEXT,
  salt TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS rep_user_email_provider ON rep_users (email, provider);
CREATE TABLE IF NOT EXISTS rep_sessions (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES rep_users(id) ON DELETE CASCADE,
  expires_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS rep_sessions_user_id ON rep_sessions(user_id);
CREATE INDEX IF NOT EXISTS rep_sessions_expires_at ON rep_sessions(expires_at);
CREATE TABLE IF NOT EXISTS rep_oauth (
  state_hash TEXT PRIMARY KEY,
  verifier TEXT NOT NULL,
  expires_at BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS rep_auth_limits (
  id TEXT PRIMARY KEY,
  attempts INTEGER NOT NULL,
  expires_at BIGINT NOT NULL
);
CREATE TABLE IF NOT EXISTS rep_accounts (
  user_id TEXT PRIMARY KEY,
  state JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
