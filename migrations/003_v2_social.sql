CREATE TABLE IF NOT EXISTS tyvon_social_activity (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES tyvon_users(id) ON DELETE CASCADE,
  display_name TEXT NOT NULL,
  workout_name TEXT NOT NULL,
  sets INTEGER NOT NULL,
  minutes INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS tyvon_social_activity_created ON tyvon_social_activity(created_at DESC);
CREATE INDEX IF NOT EXISTS tyvon_social_activity_user_created ON tyvon_social_activity(user_id,created_at DESC);
