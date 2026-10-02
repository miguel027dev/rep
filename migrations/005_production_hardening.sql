ALTER TABLE tyvon_users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE tyvon_users ADD COLUMN IF NOT EXISTS password_algo TEXT;
ALTER TABLE tyvon_users ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE tyvon_users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
UPDATE tyvon_users SET email_verified=TRUE WHERE provider='google';

CREATE TABLE IF NOT EXISTS tyvon_profiles (
  user_id TEXT PRIMARY KEY REFERENCES tyvon_users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  name TEXT NOT NULL DEFAULT 'Você',
  age INTEGER,
  weight NUMERIC(7,2),
  goal TEXT,
  experience TEXT,
  equipment JSONB NOT NULL DEFAULT '[]'::jsonb,
  days INTEGER,
  limitations TEXT NOT NULL DEFAULT 'Nenhuma',
  theme TEXT NOT NULL DEFAULT 'essential',
  complete BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tyvon_account_meta (
  user_id TEXT PRIMARY KEY REFERENCES tyvon_users(id) ON DELETE CASCADE,
  step INTEGER NOT NULL DEFAULT 0,
  revision BIGINT NOT NULL DEFAULT 1,
  messages_hash TEXT NOT NULL DEFAULT '',
  logs_hash TEXT NOT NULL DEFAULT '',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tyvon_messages (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES tyvon_users(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user','ai')),
  text TEXT NOT NULL,
  plan BOOLEAN NOT NULL DEFAULT FALSE,
  preview BOOLEAN NOT NULL DEFAULT FALSE,
  style_picker BOOLEAN NOT NULL DEFAULT FALSE,
  workouts JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, position)
);
CREATE INDEX IF NOT EXISTS tyvon_messages_user_position ON tyvon_messages(user_id, position);

CREATE TABLE IF NOT EXISTS tyvon_workout_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES tyvon_users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  occurred_at TIMESTAMPTZ NOT NULL,
  minutes NUMERIC(8,2) NOT NULL DEFAULT 1,
  sets NUMERIC(8,2) NOT NULL DEFAULT 0,
  weights JSONB NOT NULL DEFAULT '{}'::jsonb,
  feedback JSONB NOT NULL DEFAULT '{}'::jsonb,
  engine TEXT NOT NULL DEFAULT 'v1',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS tyvon_workout_logs_user_date ON tyvon_workout_logs(user_id, occurred_at DESC);

CREATE TABLE IF NOT EXISTS tyvon_workout_sets (
  id BIGSERIAL PRIMARY KEY,
  workout_id TEXT NOT NULL REFERENCES tyvon_workout_logs(id) ON DELETE CASCADE,
  exercise_id TEXT NOT NULL DEFAULT '',
  exercise_name TEXT NOT NULL DEFAULT '',
  muscle_group TEXT NOT NULL DEFAULT '',
  set_index INTEGER NOT NULL,
  weight NUMERIC(8,2) NOT NULL DEFAULT 0,
  reps INTEGER NOT NULL DEFAULT 0,
  rir NUMERIC(4,1) NOT NULL DEFAULT 2,
  target_rir NUMERIC(4,1) NOT NULL DEFAULT 2,
  completed BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS tyvon_workout_sets_workout ON tyvon_workout_sets(workout_id, set_index);

CREATE TABLE IF NOT EXISTS tyvon_email_tokens (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES tyvon_users(id) ON DELETE CASCADE,
  purpose TEXT NOT NULL CHECK (purpose IN ('verify_email','reset_password')),
  expires_at BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS tyvon_email_tokens_user ON tyvon_email_tokens(user_id);

CREATE TABLE IF NOT EXISTS tyvon_ai_limits (
  id TEXT PRIMARY KEY,
  minute_bucket BIGINT NOT NULL,
  minute_count INTEGER NOT NULL DEFAULT 0,
  day_bucket BIGINT NOT NULL,
  day_count INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tyvon_consents (
  user_id TEXT PRIMARY KEY REFERENCES tyvon_users(id) ON DELETE CASCADE,
  terms_version TEXT NOT NULL,
  privacy_version TEXT NOT NULL,
  accepted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sensitive_personalization BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER TABLE tyvon_privacy_requests ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE tyvon_privacy_requests ADD COLUMN IF NOT EXISTS notified_at TIMESTAMPTZ;
