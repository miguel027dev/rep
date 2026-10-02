import hashlib
import secrets
import time

from .db import get_db
from .emailer import send_email
from .request_security import canonical_origin


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now_ms():
    return int(time.time() * 1000)


def issue_token(user_id, purpose, ttl_ms):
    raw = secrets.token_urlsafe(40)
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tyvon_email_tokens WHERE user_id=%s AND purpose=%s", (user_id, purpose))
        cur.execute(
            "INSERT INTO tyvon_email_tokens(token_hash,user_id,purpose,expires_at) VALUES(%s,%s,%s,%s)",
            (_digest(raw), user_id, purpose, _now_ms() + ttl_ms),
        )
    return raw


def consume_token(raw, purpose):
    if not raw:
        return None
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "DELETE FROM tyvon_email_tokens WHERE token_hash=%s AND purpose=%s AND expires_at>%s RETURNING user_id",
            (_digest(raw), purpose, _now_ms()),
        )
        row = cur.fetchone()
        return row["user_id"] if row else None


def send_verification(user_id, email):
    token = issue_token(user_id, "verify_email", 24 * 3600 * 1000)
    link = f"{canonical_origin()}/api/auth/verify-email?token={token}"
    return send_email(
        email,
        "Confirme seu e-mail no TYVON",
        f"Confirme seu e-mail acessando:\n\n{link}\n\nO link expira em 24 horas.",
    )


def send_password_reset(user_id, email):
    token = issue_token(user_id, "reset_password", 30 * 60 * 1000)
    link = f"{canonical_origin()}/?reset_token={token}"
    return send_email(
        email,
        "Redefina sua senha do TYVON",
        f"Use este link para redefinir sua senha:\n\n{link}\n\nO link expira em 30 minutos.",
    )
