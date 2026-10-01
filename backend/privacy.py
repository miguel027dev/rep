import re
import secrets

from flask import Blueprint, jsonify, request

from .auth import resolve_identity, same_origin_ok
from .db import get_db

privacy_bp = Blueprint("privacy", __name__)
KINDS = {"access","correction","deletion","portability","consent","sharing","automated","other"}
EMAIL_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")


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
    if kind not in KINDS:
        return jsonify({"error": "Tipo de solicitação inválido."}), 400
    if kind == "other" and not details:
        return jsonify({"error": "Descreva sua solicitação."}), 400

    user = resolve_identity()
    protocol = "REP-LGPD-" + secrets.token_hex(5).upper()

    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS total FROM rep_privacy_requests WHERE email=%s AND created_at > NOW() - INTERVAL '24 hours'",
            (email,),
        )
        if cur.fetchone()["total"] >= 5:
            return jsonify({"error": "Limite de solicitações atingido. Tente novamente mais tarde."}), 429
        cur.execute(
            """INSERT INTO rep_privacy_requests
               (id, user_id, email, kind, details, status)
               VALUES (%s, %s, %s, %s, %s, 'received')""",
            (protocol, user["id"] if user else None, email, kind, details),
        )
    return jsonify({"ok": True, "protocol": protocol, "status": "received"}), 201
