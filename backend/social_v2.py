import json
import secrets

from flask import Blueprint, jsonify, request

from .auth import resolve_identity, same_origin_ok
from .db import get_db

social_v2_bp = Blueprint("social_v2", __name__)

@social_v2_bp.get("/api/v2/social")
def feed():
    user = resolve_identity()
    if not user:
        return jsonify({"items": []})
    try:
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("""
              SELECT id, display_name, workout_name, sets, minutes, created_at
              FROM rep_social_activity
              ORDER BY created_at DESC
              LIMIT 20
            """)
            items=[{
              "id":r["id"],"displayName":r["display_name"],"workoutName":r["workout_name"],
              "sets":r["sets"],"minutes":r["minutes"],"createdAt":r["created_at"].isoformat()
            } for r in cur.fetchall()]
        return jsonify({"items":items})
    except Exception:
        return jsonify({"items":[]})

@social_v2_bp.post("/api/v2/social")
def share():
    if not same_origin_ok():
        return jsonify({"error":"Origem não permitida."}),403
    user=resolve_identity()
    if not user:
        return jsonify({"error":"Entre na sua conta para compartilhar."}),401
    body=request.get_json(silent=True) or {}
    workout=str(body.get("workoutName") or "").strip()[:100]
    sets=int(body.get("sets") or 0);minutes=int(body.get("minutes") or 0)
    if not workout or sets<1 or sets>300 or minutes<1 or minutes>600:
        return jsonify({"error":"Resumo inválido."}),400
    try:
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("SELECT state FROM rep_accounts WHERE user_id=%s",(user["id"],))
            row=cur.fetchone();state=row["state"] if row else None
            if isinstance(state,str):state=json.loads(state)
            profile=(state or {}).get("profile") if isinstance(state,dict) else {}
            age=profile.get("age") if isinstance(profile,dict) else None
            if not isinstance(age,int) or age<18:
                return jsonify({"error":"O Circle público está disponível apenas para maiores de 18 anos."}),403
            cur.execute("SELECT COUNT(*) AS total FROM rep_social_activity WHERE user_id=%s AND created_at>NOW()-INTERVAL '24 hours'",(user["id"],))
            if cur.fetchone()["total"]>=3:
                return jsonify({"error":"Limite de 3 compartilhamentos por dia atingido."}),429
            display=str(profile.get("name") or user.get("name") or "Atleta").strip().split(" ")[0][:30] or "Atleta"
            item_id="circle_"+secrets.token_hex(8)
            cur.execute("""
              INSERT INTO rep_social_activity(id,user_id,display_name,workout_name,sets,minutes)
              VALUES(%s,%s,%s,%s,%s,%s)
            """,(item_id,user["id"],display,workout,sets,minutes))
        return jsonify({"ok":True,"id":item_id}),201
    except Exception:
        return jsonify({"error":"Não foi possível compartilhar agora."}),503
