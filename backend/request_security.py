import hmac
import os
import secrets

from flask import jsonify, request


def canonical_origin():
    configured = (os.getenv("PUBLIC_ORIGIN") or os.getenv("AUTH_BASE_URL") or "").strip().rstrip("/")
    return configured or request.host_url.rstrip("/")


def same_origin_ok():
    origin = (request.headers.get("Origin") or "").strip().rstrip("/")
    if origin:
        return hmac.compare_digest(origin, canonical_origin())
    fetch_site = (request.headers.get("Sec-Fetch-Site") or "").lower()
    if fetch_site == "cross-site" and request.method not in {"GET", "HEAD", "OPTIONS"}:
        return False
    return True


def set_csrf_cookie(response, token=None):
    value = token or request.cookies.get("tyvon_csrf") or secrets.token_urlsafe(32)
    response.set_cookie(
        "tyvon_csrf",
        value,
        max_age=30 * 86400,
        httponly=False,
        secure=request.is_secure,
        samesite="Strict",
        path="/",
    )
    return value


def require_csrf():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida.", "code": "ORIGIN_INVALID"}), 403
    cookie = request.cookies.get("tyvon_csrf", "")
    header = request.headers.get("X-CSRF-Token", "")
    if not cookie or not header or not hmac.compare_digest(cookie, header):
        return jsonify({"error": "Sessão de segurança inválida. Recarregue a página.", "code": "CSRF_INVALID"}), 403
    return None
