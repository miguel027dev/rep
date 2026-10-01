CREATE TABLE IF NOT EXISTS rep_privacy_requests (
  id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES rep_users(id) ON DELETE SET NULL,
  email TEXT NOT NULL,
  kind TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'received',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS rep_privacy_requests_email_created
  ON rep_privacy_requests (email, created_at DESC);
