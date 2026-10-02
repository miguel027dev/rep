import base64
import hashlib
import json
import os
import re
import secrets
import time
import uuid
from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, make_response, redirect, request

from .auth_tokens import consume_token, send_password_reset, send_verification
from .db import get_db
from .emailer import email_configured
from .logging_utils import log_event
from .passwords import hash_password, verify_password
from .request_security import canonical_origin, require_csrf, same_origin_ok, set_csrf_cookie

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
TERMS_VERSION = "2026-10-01"
PRIVACY_VERSION = "2026-10-01"


def now_ms():
    return int(time.time() * 1000)


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def set_cookie(resp, key, value, seconds):
    resp.set_cookie(key, value, max_age=seconds, httponly=True, secure=request.is_secure, samesite="Lax", path="/")


def clear_cookie(resp, key):
    resp.delete_cookie(key, path="/", secure=request.is_secure, httponly=True, samesite="Lax")


def cleanup_expired(conn):
    now = now_ms()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tyvon_sessions WHERE expires_at<=%s", (now,))
        cur.execute("DELETE FROM tyvon_oauth WHERE expires_at<=%s", (now,))
        cur.execute("DELETE FROM tyvon_auth_limits WHERE expires_at<=%s", (now,))
        cur.execute("DELETE FROM tyvon_email_tokens WHERE expires_at<=%s", (now,))


def resolve_identity():
    token = request.cookies.get("tyvon_session", "")
    if not token:
        return None
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("""
          SELECT u.id,u.email,u.name,u.provider,u.email_verified
          FROM tyvon_users u
          JOIN tyvon_sessions s ON s.user_id=u.id
          WHERE s.token_hash=%s AND s.expires_at>%s
        """, (digest(token), now_ms()))
        row = cur.fetchone()
        return dict(row) if row else None


def new_session(user_id):
    token = secrets.token_urlsafe(48)
    with get_db() as conn:
        cleanup_expired(conn)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tyvon_sessions(token_hash,user_id,expires_at) VALUES(%s,%s,%s)",
                (digest(token), user_id, now_ms() + 30 * 86400000),
            )
            cur.execute("""
              DELETE FROM tyvon_sessions
              WHERE user_id=%s AND token_hash NOT IN (
                SELECT token_hash FROM tyvon_sessions WHERE user_id=%s ORDER BY expires_at DESC LIMIT 8
              )
            """, (user_id, user_id))
    return token


def action_rate_limit(conn, purpose, identity, limit=3, window_ms=3600000):
    key = digest("action|" + purpose + "|" + identity + "|" + (request.remote_addr or "unknown"))
    now = now_ms()
    with conn.cursor() as cur:
        cur.execute("SELECT attempts,expires_at FROM tyvon_auth_limits WHERE id=%s", (key,))
        row = cur.fetchone()
        if row and row["expires_at"] > now and row["attempts"] >= limit:
            return False
        cur.execute("""
          INSERT INTO tyvon_auth_limits(id,attempts,expires_at) VALUES(%s,1,%s)
          ON CONFLICT(id) DO UPDATE SET
            attempts=CASE WHEN tyvon_auth_limits.expires_at<=%s THEN 1 ELSE tyvon_auth_limits.attempts+1 END,
            expires_at=CASE WHEN tyvon_auth_limits.expires_at<=%s THEN EXCLUDED.expires_at ELSE tyvon_auth_limits.expires_at END
        """, (key, now + window_ms, now, now))
    return True


def google_configured():
    return bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))


def redirect_uri():
    return f"{(os.getenv('AUTH_BASE_URL') or canonical_origin()).rstrip('/')}/api/auth/google/callback"


def credentials_body():
    if "application/json" not in (request.content_type or ""):
        return None, (jsonify({"error": "Envie os dados em JSON."}), 415)
    raw = request.get_data(cache=False)
    if len(raw) > 4096:
        return None, (jsonify({"error": "Dados muito longos."}), 413)
    try:
        body = json.loads(raw)
    except Exception:
        return None, (jsonify({"error": "Dados inválidos."}), 400)
    return body if isinstance(body, dict) else {}, None


def auth_rate_limit(conn, email):
    key = digest(email + "|" + (request.remote_addr or "unknown"))
    now = now_ms()
    with conn.cursor() as cur:
        cur.execute("SELECT attempts,expires_at FROM tyvon_auth_limits WHERE id=%s", (key,))
        rate = cur.fetchone()
        if rate and rate["expires_at"] > now and rate["attempts"] >= 8:
            return False, key
        cur.execute("""
          INSERT INTO tyvon_auth_limits(id,attempts,expires_at) VALUES(%s,1,%s)
          ON CONFLICT(id) DO UPDATE SET
            attempts=CASE WHEN tyvon_auth_limits.expires_at<=%s THEN 1 ELSE tyvon_auth_limits.attempts+1 END,
            expires_at=CASE WHEN tyvon_auth_limits.expires_at<=%s THEN EXCLUDED.expires_at ELSE tyvon_auth_limits.expires_at END
        """, (key, now + 900000, now, now))
    return True, key


@auth_bp.get("/status")
def status():
    resp = make_response(jsonify({
        "email": True,
        "google": google_configured(),
        "emailVerification": email_configured(),
    }))
    set_csrf_cookie(resp)
    return resp


@auth_bp.get("/google")
def google_start():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    if not google_configured():
        return jsonify({"error": "O login Google ainda aguarda configuração. Use e-mail e senha."}), 503
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    with get_db() as conn:
        cleanup_expired(conn)
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tyvon_oauth(state_hash,verifier,expires_at) VALUES(%s,%s,%s)", (digest(state), verifier, now_ms()+600000))
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "prompt": "select_account",
    }
    resp = redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params), code=302)
    set_cookie(resp, "tyvon_oauth", state, 600)
    set_csrf_cookie(resp)
    return resp


@auth_bp.get("/google/callback")
def google_callback():
    try:
        state = request.args.get("state", "")
        code = request.args.get("code", "")
        cookie_state = request.cookies.get("tyvon_oauth", "")
        if not google_configured() or not state or not code or not cookie_state or state != cookie_state:
            raise RuntimeError("invalid oauth callback")
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM tyvon_oauth WHERE state_hash=%s AND expires_at>%s RETURNING verifier", (digest(state), now_ms()))
            flow = cur.fetchone()
        if not flow:
            raise RuntimeError("expired oauth state")
        token_resp = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code,
            "code_verifier": flow["verifier"],
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri(),
        }, timeout=20)
        token_data = token_resp.json()
        if not token_resp.ok or not token_data.get("access_token"):
            raise RuntimeError("google token failed")
        info_resp = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": "Bearer " + token_data["access_token"]},
            timeout=20,
        )
        person = info_resp.json()
        if not info_resp.ok or not person.get("sub") or person.get("email_verified") is not True or not person.get("email"):
            raise RuntimeError("google userinfo failed")
        email = str(person["email"]).strip().lower()
        name = str(person.get("given_name") or "")[:40]
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM tyvon_users WHERE google_sub=%s", (person["sub"],))
            user = cur.fetchone()
            if not user:
                cur.execute("SELECT * FROM tyvon_users WHERE email=%s ORDER BY (password_hash IS NOT NULL) DESC, created_at ASC LIMIT 1", (email,))
                user = cur.fetchone()
                if user:
                    cur.execute(
                        "UPDATE tyvon_users SET google_sub=%s,email_verified=TRUE,name=CASE WHEN name='' THEN %s ELSE name END,updated_at=NOW() WHERE id=%s",
                        (person["sub"], name, user["id"]),
                    )
                    user = dict(user)
                    user["email_verified"] = True
                else:
                    user_id = "tyvon_" + str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO tyvon_users(id,email,name,provider,google_sub,email_verified) VALUES(%s,%s,%s,'google',%s,TRUE)",
                        (user_id, email, name, person["sub"]),
                    )
                    user = {"id": user_id, "email": email, "name": name, "provider": "google", "email_verified": True}
        session = new_session(user["id"])
        resp = redirect("/?welcome=google", code=302)
        set_cookie(resp, "tyvon_session", session, 30*86400)
        clear_cookie(resp, "tyvon_oauth")
        set_csrf_cookie(resp, secrets.token_urlsafe(32))
        return resp
    except Exception as exc:
        log_event("warning", "google_auth_failed", error=type(exc).__name__)
        resp = redirect("/?auth_error=google", code=302)
        clear_cookie(resp, "tyvon_oauth")
        return resp


@auth_bp.get("/verify-email")
def verify_email():
    user_id = consume_token(request.args.get("token", ""), "verify_email")
    if user_id:
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("UPDATE tyvon_users SET email_verified=TRUE,updated_at=NOW() WHERE id=%s", (user_id,))
    return redirect("/?email_verified=" + ("1" if user_id else "0"), code=302)


@auth_bp.post("/resend-verification")
def resend_verification():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    body = request.get_json(silent=True) or {}
    email = str(body.get("email") or "").strip().lower()
    if EMAIL_RE.match(email):
        with get_db() as conn:
            if not action_rate_limit(conn, "verify_email", email):
                return jsonify({"error": "Muitas solicitações. Tente novamente mais tarde.", "code": "RATE_LIMIT"}), 429
            with conn.cursor() as cur:
                cur.execute("SELECT id,email_verified FROM tyvon_users WHERE email=%s AND password_hash IS NOT NULL LIMIT 1", (email,))
                user = cur.fetchone()
        sent = bool(user and not user["email_verified"] and send_verification(user["id"], email))
        return jsonify({"ok": True, "sent": sent, "message": "Se houver uma conta pendente e o envio estiver disponível, enviaremos um novo link."})
    return jsonify({"ok": True, "sent": False, "message": "Se houver uma conta pendente e o envio estiver disponível, enviaremos um novo link."})


@auth_bp.post("/forgot-password")
def forgot_password():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    body = request.get_json(silent=True) or {}
    email = str(body.get("email") or "").strip().lower()
    if EMAIL_RE.match(email):
        with get_db() as conn:
            if not action_rate_limit(conn, "reset_password", email):
                return jsonify({"error": "Muitas solicitações. Tente novamente mais tarde.", "code": "RATE_LIMIT"}), 429
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM tyvon_users WHERE email=%s AND password_hash IS NOT NULL LIMIT 1", (email,))
                user = cur.fetchone()
        if user:
            send_password_reset(user["id"], email)
    return jsonify({"ok": True, "message": "Se esse e-mail estiver cadastrado e o envio estiver disponível, enviaremos as instruções."})


@auth_bp.post("/reset-password")
def reset_password():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    body = request.get_json(silent=True) or {}
    password = body.get("password")
    if not isinstance(password, str) or not 10 <= len(password) <= 128:
        return jsonify({"error": "Use uma senha de 10 a 128 caracteres."}), 400
    user_id = consume_token(str(body.get("token") or ""), "reset_password")
    if not user_id:
        return jsonify({"error": "Este link expirou ou já foi usado."}), 400
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE tyvon_users SET password_hash=%s,password_algo='argon2id',salt=NULL,updated_at=NOW() WHERE id=%s",
            (hash_password(password), user_id),
        )
        cur.execute("DELETE FROM tyvon_sessions WHERE user_id=%s", (user_id,))
    return jsonify({"ok": True})


@auth_bp.post("/logout")
def logout():
    error = require_csrf()
    if error:
        return error
    token = request.cookies.get("tyvon_session", "")
    if token:
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM tyvon_sessions WHERE token_hash=%s", (digest(token),))
    resp = make_response(jsonify({"ok": True}))
    clear_cookie(resp, "tyvon_session")
    set_csrf_cookie(resp, secrets.token_urlsafe(32))
    return resp


def auth_action(mode):
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    body, error = credentials_body()
    if error:
        return error
    email = str(body.get("email") or "").strip().lower()
    password = body.get("password")
    if not EMAIL_RE.match(email) or len(email) > 254 or not isinstance(password, str) or not 10 <= len(password) <= 128:
        return jsonify({"error": "Use um e-mail válido e uma senha de 10 a 128 caracteres."}), 400
    with get_db() as conn:
        cleanup_expired(conn)
        allowed, rate_key = auth_rate_limit(conn, email)
        if not allowed:
            return jsonify({"error": "Muitas tentativas. Aguarde 15 minutos.", "code": "RATE_LIMIT"}), 429
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tyvon_users WHERE email=%s ORDER BY (password_hash IS NOT NULL) DESC, created_at ASC LIMIT 1", (email,))
            user = cur.fetchone()
            if mode == "register":
                if body.get("accepted") is not True:
                    return jsonify({"error": "Confirme que você tem pelo menos 14 anos e aceita os Termos e a Política de Privacidade."}), 400
                if user and user.get("password_hash"):
                    return jsonify({"error": "Este e-mail já tem uma conta. Entre com sua senha."}), 409
                password_value = hash_password(password)
                if user:
                    user = dict(user)
                    cur.execute(
                        "UPDATE tyvon_users SET password_hash=%s,password_algo='argon2id',salt=NULL,updated_at=NOW() WHERE id=%s",
                        (password_value, user["id"]),
                    )
                    user["password_hash"] = password_value
                else:
                    user_id = "tyvon_" + str(uuid.uuid4())
                    cur.execute(
                        "INSERT INTO tyvon_users(id,email,name,provider,password_hash,password_algo,email_verified) VALUES(%s,%s,'','password',%s,'argon2id',FALSE)",
                        (user_id, email, password_value),
                    )
                    user = {"id": user_id, "email": email, "name": "", "provider": "password", "email_verified": False, "password_hash": password_value}
                cur.execute(
                    "INSERT INTO tyvon_consents(user_id,terms_version,privacy_version,sensitive_personalization) VALUES(%s,%s,%s,FALSE) ON CONFLICT(user_id) DO NOTHING",
                    (user["id"], TERMS_VERSION, PRIVACY_VERSION),
                )
            else:
                if not user:
                    return jsonify({"error": "E-mail ou senha incorretos."}), 401
                ok, replacement = verify_password(user["password_hash"], password, user.get("salt"))
                if not ok:
                    return jsonify({"error": "E-mail ou senha incorretos."}), 401
                if replacement:
                    cur.execute(
                        "UPDATE tyvon_users SET password_hash=%s,password_algo='argon2id',salt=NULL,updated_at=NOW() WHERE id=%s",
                        (replacement, user["id"]),
                    )
                user = dict(user)
            cur.execute("DELETE FROM tyvon_auth_limits WHERE id=%s", (rate_key,))
    if mode == "register":
        send_verification(user["id"], email)
    session = new_session(user["id"])
    resp = make_response(jsonify({
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name") or "",
            "provider": user.get("provider") or "password",
            "emailVerified": bool(user.get("email_verified")),
        },
        "verificationSent": bool(mode == "register" and email_configured()),
    }))
    set_cookie(resp, "tyvon_session", session, 30*86400)
    set_csrf_cookie(resp, secrets.token_urlsafe(32))
    return resp


@auth_bp.post("/register")
def register():
    return auth_action("register")


@auth_bp.post("/login")
def login():
    return auth_action("login")
