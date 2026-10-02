import hmac
import os
import re
import secrets

import requests
from flask import Blueprint, jsonify, request

from .auth import resolve_identity
from .db import get_db
from .logging_utils import log_event
from .request_security import require_csrf, same_origin_ok
from .validation import PRIVACY_KINDS

privacy_bp = Blueprint("privacy", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _notify_privacy_team(payload):
    url = (os.getenv("PRIVACY_WEBHOOK_URL") or "").strip()
    if not url:
        return False
    try:
        response = requests.post(url, json=payload, timeout=8)
        return response.ok
    except requests.RequestException as exc:
        log_event("warning", "privacy_webhook_failed", error=type(exc).__name__)
        return False


@privacy_bp.post("/api/privacy/requests")
def create_privacy_request():
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    if "application/json" not in (request.content_type or ""):
        return jsonify({"error": "Envie a solicitação em JSON."}), 415
    body = request.get_json(silent=True) or {}
    email = str(body.get("email") or "").strip().lower()[:254]
    kind = str(body.get("kind") or "").strip()
    details = str(body.get("details") or "").strip()[:4000]
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Informe um e-mail válido."}), 400
    if kind not in PRIVACY_KINDS:
        return jsonify({"error": "Tipo de solicitação inválido."}), 400
    if kind == "other" and not details:
        return jsonify({"error": "Descreva sua solicitação."}), 400

    user = resolve_identity()
    protocol = "TYVON-LGPD-" + secrets.token_hex(5).upper()
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS total FROM tyvon_privacy_requests WHERE email=%s AND created_at>NOW()-INTERVAL '24 hours'",
            (email,),
        )
        if cur.fetchone()["total"] >= 5:
            return jsonify({"error": "Limite de solicitações atingido. Tente novamente mais tarde."}), 429
        cur.execute("""
          INSERT INTO tyvon_privacy_requests(id,user_id,email,kind,details,status,updated_at)
          VALUES(%s,%s,%s,%s,%s,'received',NOW())
        """, (protocol, user["id"] if user else None, email, kind, details))

    notified = _notify_privacy_team({
        "protocol": protocol,
        "kind": kind,
        "email": email,
        "details": details,
        "source": "tyvon",
    })
    if notified:
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("UPDATE tyvon_privacy_requests SET notified_at=NOW() WHERE id=%s", (protocol,))
    log_event("info", "privacy_request_created", protocol=protocol, kind=kind, notified=notified)
    return jsonify({"ok": True, "protocol": protocol, "status": "received"}), 201


@privacy_bp.get("/api/privacy/requests/me")
def my_privacy_requests():
    user = resolve_identity()
    if not user:
        return jsonify({"error": "Entre na sua conta.", "code": "SIGN_IN_REQUIRED"}), 401
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("""
          SELECT id,kind,status,created_at,updated_at
          FROM tyvon_privacy_requests
          WHERE user_id=%s OR email=%s
          ORDER BY created_at DESC
          LIMIT 30
        """, (user["id"], user["email"]))
        items = [{
            "protocol": row["id"],
            "kind": row["kind"],
            "status": row["status"],
            "createdAt": row["created_at"].isoformat(),
            "updatedAt": row["updated_at"].isoformat(),
        } for row in cur.fetchall()]
    return jsonify({"items": items})


@privacy_bp.patch("/api/privacy/requests/<protocol>")
def update_privacy_request(protocol):
    admin_token = (os.getenv("PRIVACY_ADMIN_TOKEN") or "").strip()
    supplied = request.headers.get("X-Privacy-Admin-Token", "")
    if not admin_token or not supplied or not hmac.compare_digest(admin_token, supplied):
        return jsonify({"error": "Acesso não autorizado."}), 401
    body = request.get_json(silent=True) or {}
    status = str(body.get("status") or "").strip()
    if status not in {"received", "in_review", "completed", "rejected"}:
        return jsonify({"error": "Status inválido."}), 400
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE tyvon_privacy_requests SET status=%s,updated_at=NOW() WHERE id=%s RETURNING id",
            (status, protocol),
        )
        if not cur.fetchone():
            return jsonify({"error": "Protocolo não encontrado."}), 404
    log_event("info", "privacy_request_updated", protocol=protocol, status=status)
    return jsonify({"ok": True, "protocol": protocol, "status": status})
