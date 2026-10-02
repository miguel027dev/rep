UPDATE tyvon_workout_logs SET engine='tyvon' WHERE engine IN ('v1','v2','rep','REP');
ALTER TABLE tyvon_workout_logs ALTER COLUMN engine SET DEFAULT 'tyvon';
