import base64
import hashlib
import hmac
import os
import secrets
import time
import uuid
from urllib.parse import urlencode

import requests
from flask import Blueprint, jsonify, make_response, redirect, request

from .db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def now_ms():
    return int(time.time() * 1000)


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000, dklen=32).hex()


def cookie_secure():
    return request.is_secure or request.headers.get("X-Forwarded-Proto", "").split(",")[0].strip() == "https"


def set_cookie(resp, key, value, seconds):
    resp.set_cookie(key, value, max_age=seconds, httponly=True, secure=cookie_secure(), samesite="Lax", path="/")


def clear_cookie(resp, key):
    resp.delete_cookie(key, path="/", secure=cookie_secure(), httponly=True, samesite="Lax")


def same_origin_ok():
    origin = request.headers.get("Origin")
    if not origin:
        return True
    forwarded = request.headers.get("X-Forwarded-Proto", request.scheme).split(",")[0].strip()
    host = request.headers.get("X-Forwarded-Host", request.host).split(",")[0].strip()
    return origin.rstrip("/") == f"{forwarded}://{host}".rstrip("/")


def resolve_identity():
    token = request.cookies.get("rep_session", "")
    if token:
        try:
            with get_db() as conn, conn.cursor() as cur:
                cur.execute("""
                  SELECT u.id, u.email, u.name, u.provider
                  FROM rep_users u JOIN rep_sessions s ON s.user_id = u.id
                  WHERE s.token_hash = %s AND s.expires_at > %s
                """, (digest(token), now_ms()))
                row = cur.fetchone()
                if row:
                    return dict(row)
        except Exception:
            return None
    return None


def new_session(user_id):
    token = secrets.token_hex(32)
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO rep_sessions (token_hash, user_id, expires_at) VALUES (%s, %s, %s)", (digest(token), user_id, now_ms() + 30 * 86400000))
    return token


def google_configured():
    return bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))


def redirect_uri():
    base = os.getenv("AUTH_BASE_URL", "").rstrip("/")
    if not base:
        forwarded = request.headers.get("X-Forwarded-Proto", request.scheme).split(",")[0].strip()
        host = request.headers.get("X-Forwarded-Host", request.host).split(",")[0].strip()
        base = f"{forwarded}://{host}"
    return f"{base}/api/auth/google/callback"


@auth_bp.get("/status")
def status():
    return jsonify({"email": True, "google": google_configured()})


@auth_bp.get("/google")
def google_start():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    if not google_configured():
        return jsonify({"error": "O login Google ainda aguarda configuração. Use e-mail e senha."}), 503
    try:
        state = secrets.token_hex(32)
        verifier = secrets.token_hex(32)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO rep_oauth (state_hash, verifier, expires_at) VALUES (%s,%s,%s)", (digest(state), verifier, now_ms() + 600000))
        params = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"), "redirect_uri": redirect_uri(), "response_type": "code",
            "scope": "openid email profile", "state": state, "code_challenge": challenge, "code_challenge_method": "S256", "prompt": "select_account",
        }
        resp = redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params), code=302)
        set_cookie(resp, "rep_oauth", state, 600)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception:
        return jsonify({"error": "Não foi possível iniciar o login."}), 503


@auth_bp.get("/google/callback")
def google_callback():
    try:
        state = request.args.get("state", "")
        code = request.args.get("code", "")
        if not google_configured() or not state or not code or state != request.cookies.get("rep_oauth", ""):
            raise RuntimeError("invalid oauth callback")
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM rep_oauth WHERE state_hash=%s AND expires_at>%s RETURNING verifier", (digest(state), now_ms()))
            flow = cur.fetchone()
        if not flow:
            raise RuntimeError("expired oauth state")
        token_resp = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": os.getenv("GOOGLE_CLIENT_ID"), "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "code": code, "code_verifier": flow["verifier"], "grant_type": "authorization_code", "redirect_uri": redirect_uri(),
        }, timeout=20)
        data = token_resp.json()
        if not token_resp.ok or not data.get("access_token"):
            raise RuntimeError("google token failed")
        info_resp = requests.get("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": "Bearer " + data["access_token"]}, timeout=20)
        person = info_resp.json()
        if not info_resp.ok or not person.get("sub") or person.get("email_verified") is not True or not person.get("email"):
            raise RuntimeError("google userinfo failed")
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("SELECT id,email,name,provider FROM rep_users WHERE google_sub=%s", (person["sub"],))
            user = cur.fetchone()
            if not user:
                user_id = "rep_" + str(uuid.uuid4())
                email = person["email"].lower()
                name = str(person.get("given_name") or "")[:40]
                cur.execute("INSERT INTO rep_users (id,email,name,provider,google_sub) VALUES (%s,%s,%s,'google',%s)", (user_id, email, name, person["sub"]))
                user = {"id": user_id, "email": email, "name": name, "provider": "google"}
        session_token = new_session(user["id"])
        resp = redirect("/?welcome=google", code=302)
        set_cookie(resp, "rep_session", session_token, 30 * 86400)
        set_cookie(resp, "rep_local", "1", 30 * 86400)
        clear_cookie(resp, "rep_oauth")
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception:
        resp = redirect("/?auth_error=google", code=302)
        resp.headers["Cache-Control"] = "no-store"
        return resp


@auth_bp.post("/logout")
def logout():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    try:
        token = request.cookies.get("rep_session", "")
        if token:
            with get_db() as conn, conn.cursor() as cur:
                cur.execute("DELETE FROM rep_sessions WHERE token_hash=%s", (digest(token),))
        resp = make_response(jsonify({"ok": True}))
        clear_cookie(resp, "rep_session")
        set_cookie(resp, "rep_local", "1", 30 * 86400)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception:
        return jsonify({"error": "Não foi possível sair."}), 503


def _credentials_body():
    if "application/json" not in (request.content_type or ""):
        return None, (jsonify({"error": "Envie os dados em JSON."}), 415)
    raw = request.get_data(cache=False)
    if len(raw) > 4096:
        return None, (jsonify({"error": "Dados muito longos."}), 413)
    try:
        return __import__("json").loads(raw), None
    except Exception:
        return None, (jsonify({"error": "Dados inválidos."}), 400)


def _auth_action(mode):
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    body, error = _credentials_body()
    if error:
        return error
    email = str(body.get("email") or "").strip().lower()
    password = body.get("password")
    import re
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) or len(email) > 254 or not isinstance(password, str) or len(password) < 10 or len(password) > 128:
        return jsonify({"error": "Use um e-mail válido e uma senha de 10 a 128 caracteres."}), 400
    try:
        ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For", "unknown").split(",")[0].strip()
        rate_key = digest(email + "|" + ip)
        now = now_ms()
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("SELECT attempts,expires_at FROM rep_auth_limits WHERE id=%s", (rate_key,))
            rate = cur.fetchone()
            if rate and rate["expires_at"] > now and rate["attempts"] >= 8:
                return jsonify({"error": "Muitas tentativas. Aguarde 15 minutos."}), 429
            cur.execute("""
              INSERT INTO rep_auth_limits (id,attempts,expires_at) VALUES (%s,1,%s)
              ON CONFLICT(id) DO UPDATE SET
                attempts=CASE WHEN rep_auth_limits.expires_at <= %s THEN 1 ELSE rep_auth_limits.attempts + 1 END,
                expires_at=CASE WHEN rep_auth_limits.expires_at <= %s THEN EXCLUDED.expires_at ELSE rep_auth_limits.expires_at END
            """, (rate_key, now + 900000, now, now))
            cur.execute("SELECT * FROM rep_users WHERE email=%s AND provider='password'", (email,))
            user = cur.fetchone()
            if mode == "register":
                if body.get("accepted") is not True:
                    return jsonify({"error": "Confirme que você tem pelo menos 13 anos e aceita salvar seu perfil."}), 400
                if user:
                    return jsonify({"error": "Este e-mail já tem uma conta. Entre com sua senha."}), 409
                salt = secrets.token_hex(32)
                pw_hash = password_hash(password, salt)
                user = {"id": "rep_" + str(uuid.uuid4()), "email": email, "name": "", "provider": "password"}
                cur.execute("INSERT INTO rep_users (id,email,name,provider,password_hash,salt) VALUES (%s,%s,'','password',%s,%s)", (user["id"], email, pw_hash, salt))
            else:
                candidate = password_hash(password, user["salt"] if user else "rep-invalid-login-salt")
                expected = user["password_hash"] if user else "0" * 64
                if not user or not hmac.compare_digest(candidate, expected):
                    return jsonify({"error": "E-mail ou senha incorretos."}), 401
            cur.execute("DELETE FROM rep_auth_limits WHERE id=%s", (rate_key,))
        token = new_session(user["id"])
        resp = make_response(jsonify({"user": {"id": user["id"], "email": user["email"], "name": user["name"], "provider": user["provider"]}}))
        set_cookie(resp, "rep_session", token, 30 * 86400)
        set_cookie(resp, "rep_local", "1", 30 * 86400)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception:
        return jsonify({"error": "Não foi possível acessar sua conta. Tente novamente."}), 503


@auth_bp.post("/register")
def register():
    return _auth_action("register")


@auth_bp.post("/login")
def login():
    return _auth_action("login")
