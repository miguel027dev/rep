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
