import os
import secrets

import psycopg
from flask import Flask, g, jsonify, redirect, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.account import account_bp
from backend.auth import auth_bp
from backend.chat import chat_bp
from backend.db import DatabaseUnavailable, ping_db
from backend.logging_utils import log_event
from backend.privacy import privacy_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 1_100_000
proxy_hops = max(0, min(2, int(os.getenv("TRUST_PROXY_HOPS", "1"))))
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=proxy_hops, x_proto=proxy_hops, x_host=proxy_hops, x_port=proxy_hops)

app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(privacy_bp)


@app.before_request
def attach_request_id():
    supplied = (request.headers.get("X-Request-ID") or "").strip()
    g.request_id = supplied[:80] if supplied and all(c.isalnum() or c in "-_." for c in supplied) else secrets.token_hex(10)


@app.after_request
def harden_response(response):
    response.headers["X-Request-ID"] = getattr(g, "request_id", "")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.errorhandler(DatabaseUnavailable)
def database_unavailable(exc):
    log_event("error", "database_unavailable", error=str(exc))
    return jsonify({"error": "O serviço de dados está indisponível. Tente novamente.", "code": "DATABASE_UNAVAILABLE"}), 503


@app.errorhandler(psycopg.Error)
def postgres_error(exc):
    log_event("error", "postgres_error", error=type(exc).__name__)
    return jsonify({"error": "O serviço de dados está indisponível. Tente novamente.", "code": "DATABASE_UNAVAILABLE"}), 503


@app.errorhandler(413)
def too_large(_exc):
    return jsonify({"error": "A solicitação excede o limite permitido.", "code": "PAYLOAD_TOO_LARGE"}), 413


@app.errorhandler(Exception)
def unexpected_error(exc):
    log_event("error", "unhandled_exception", error=type(exc).__name__)
    return jsonify({"error": "Ocorreu um erro inesperado.", "code": "INTERNAL_ERROR"}), 500


@app.get("/api/health/live")
def health_live():
    return jsonify({"ok": True, "service": "tyvon"})


@app.get("/api/health/ready")
@app.get("/api/health")
def health_ready():
    try:
        database = ping_db()
    except Exception as exc:
        log_event("warning", "readiness_failed", error=type(exc).__name__)
        return jsonify({"ok": False, "service": "tyvon", "database": False}), 503
    return jsonify({"ok": bool(database), "service": "tyvon", "database": bool(database)})


@app.get("/signin-with-chatgpt")
def legacy_signin_redirect():
    return redirect("/", code=308)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_app(path):
    if path.startswith("api/"):
        return jsonify({"error": "Recurso não encontrado."}), 404
    if path:
        target = os.path.join(DIST_DIR, path)
        if os.path.isfile(target):
            response = send_from_directory(DIST_DIR, path)
            if "/assets/" in "/" + path:
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            return response
    return send_from_directory(DIST_DIR, "index.html")


if __name__ == "__main__":
    from backend.migrate import run_migrations
    run_migrations()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
