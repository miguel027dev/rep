import json
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from psycopg.types.json import Jsonb

from .auth import resolve_identity, same_origin_ok
from .db import get_db
from .workouts import sanitize_workout_cards

account_bp = Blueprint("account", __name__)


def string(v, max_len):
    return v.strip()[:max_len] if isinstance(v, str) else ""


def validate_account_state(raw, email):
    if not isinstance(raw, dict) or not isinstance(raw.get("profile"), dict) or not isinstance(raw.get("step"), int) or not 0 <= raw["step"] <= 8:
        raise ValueError("Perfil inválido.")
    p = raw["profile"]
    profile = {
        "email": email,
        "name": string(p.get("name"), 40) or "Você",
        "complete": p.get("complete") is True,
        "equipment": [string(x, 40) for x in (p.get("equipment") or [])[:8]] if isinstance(p.get("equipment"), list) else [],
    }
    if "theme" in p and p["theme"] not in ["essential", "energy"]:
        raise ValueError("Estilo inválido.")
    profile["theme"] = p.get("theme") or "essential"
    version = p.get("experienceVersion") or "v1"
    if version not in ["v1", "v2"]:
        raise ValueError("Versão da experiência inválida.")
    profile["experienceVersion"] = version
    if "sessionMinutes" in p:
        if not isinstance(p["sessionMinutes"], int) or not 25 <= p["sessionMinutes"] <= 75:
            raise ValueError("Duração de sessão inválida.")
        profile["sessionMinutes"] = p["sessionMinutes"]
    else:
        profile["sessionMinutes"] = 50
    allowed_priorities = {"Peitoral","Costas","Pernas","Posterior","Glúteos","Ombros","Bíceps","Tríceps","Panturrilha"}
    if isinstance(p.get("priorityMuscles"), list):
        profile["priorityMuscles"] = [string(x, 40) for x in p["priorityMuscles"][:3] if string(x,40) in allowed_priorities]
    else:
        profile["priorityMuscles"] = []
    if "age" in p:
        if not isinstance(p["age"], int) or not 13 <= p["age"] <= 100:
            raise ValueError("O REP está disponível a partir de 13 anos.")
        profile["age"] = p["age"]
    if "weight" in p:
        if not isinstance(p["weight"], (int, float)) or isinstance(p["weight"], bool) or not 30 <= p["weight"] <= 350:
            raise ValueError("Peso inválido.")
        profile["weight"] = p["weight"]
    for key in ["goal", "experience", "limitations"]:
        if key in p:
            profile[key] = string(p.get(key), 500 if key == "limitations" else 120)
    if "days" in p:
        if not isinstance(p["days"], int) or not 2 <= p["days"] <= 5:
            raise ValueError("Frequência inválida.")
        profile["days"] = p["days"]
    if profile["complete"] and not all([profile.get("age"), profile.get("weight"), profile.get("goal"), profile.get("experience"), profile.get("days"), profile["equipment"], profile.get("limitations")]):
        raise ValueError("Conclua as perguntas do perfil.")
    if profile.get("age", 18) < 18 and profile.get("goal") == "Perder gordura":
        profile["goal"] = "Criar uma rotina"

    messages = []
    if isinstance(raw.get("messages"), list):
        for m in raw["messages"][-200:]:
            if not isinstance(m, dict):
                continue
            text = string(m.get("text"), 16000)
            if not text:
                continue
            out = {"role": "user" if m.get("role") == "user" else "ai", "text": text}
            if m.get("plan"): out["plan"] = True
            if m.get("preview"): out["preview"] = True
            if m.get("role") != "user" and m.get("stylePicker") is True: out["stylePicker"] = True
            if m.get("role") != "user" and isinstance(m.get("workouts"), list) and m["workouts"]:
                cards = sanitize_workout_cards(m["workouts"])
                if cards: out["workouts"] = cards
            messages.append(out)

    logs = []
    if isinstance(raw.get("logs"), list):
        for l in raw["logs"][-500:]:
            if not isinstance(l, dict):
                continue
            weights = {}
            if isinstance(l.get("weights"), dict):
                for k, v in list(l["weights"].items())[:100]:
                    weights[string(k, 20)] = string(str(v), 20)
            set_logs = []
            if isinstance(l.get("setLogs"), list):
                for s in l["setLogs"][:160]:
                    if not isinstance(s, dict):
                        continue
                    reps = min(100, max(0, int(float(s.get("reps") or 0))))
                    weight = min(500, max(0, float(s.get("weight") or 0)))
                    rir = min(5, max(0, float(s.get("rir") if s.get("rir") is not None else 2)))
                    if reps <= 0:
                        continue
                    set_logs.append({
                        "exerciseId": string(s.get("exerciseId"), 80),
                        "exerciseName": string(s.get("exerciseName"), 100),
                        "group": string(s.get("group"), 60),
                        "setIndex": min(20, max(1, int(float(s.get("setIndex") or 1)))),
                        "weight": weight, "reps": reps, "rir": rir,
                        "targetRir": min(5, max(0, float(s.get("targetRir") if s.get("targetRir") is not None else rir))),
                        "completed": s.get("completed") is True,
                    })
            feedback = {}
            if isinstance(l.get("feedback"), dict):
                effort = l["feedback"].get("effort")
                if isinstance(effort, (int, float)) and 1 <= effort <= 5:
                    feedback["effort"] = int(effort)
            logs.append({
                "id": string(l.get("id"), 80), "name": string(l.get("name"), 120), "date": string(l.get("date"), 40),
                "minutes": min(600, max(1, float(l.get("minutes") or 1))), "sets": min(300, max(0, float(l.get("sets") or 0))),
                "weights": weights, "setLogs": set_logs, "feedback": feedback,
                "engine": "v2" if l.get("engine") == "v2" else "v1",
            })
    return {"profile": profile, "messages": messages, "logs": logs, "step": raw["step"]}


@account_bp.route("/api/account", methods=["GET", "POST", "PUT", "DELETE"])
def account():
    user = resolve_identity()
    if not user:
        return jsonify({"error": "Entre com sua conta para continuar.", "code": "SIGN_IN_REQUIRED"}), 401
    if not same_origin_ok():
        return jsonify({"error": "Origem não permitida."}), 403
    try:
        with get_db() as conn, conn.cursor() as cur:
            if request.method == "GET":
                cur.execute("SELECT state FROM rep_accounts WHERE user_id=%s", (user["id"],))
                row = cur.fetchone()
                state = row["state"] if row else None
                if isinstance(state, str): state = json.loads(state)
                return jsonify({"user": user, "state": state})
            if request.method == "DELETE":
                cur.execute("DELETE FROM rep_accounts WHERE user_id=%s", (user["id"],))
                return jsonify({"ok": True})
            if "application/json" not in (request.content_type or ""):
                return jsonify({"error": "Envie os dados em JSON."}), 415
            raw_bytes = request.get_data(cache=False)
            if len(raw_bytes) > 1_000_000:
                return jsonify({"error": "Seu histórico está muito grande."}), 413
            try:
                state = validate_account_state(json.loads(raw_bytes), user["email"])
            except json.JSONDecodeError:
                return jsonify({"error": "Dados inválidos."}), 400
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            ts = datetime.now(timezone.utc)
            if request.method == "POST":
                cur.execute("INSERT INTO rep_accounts (user_id,state,updated_at) VALUES (%s,%s,%s) ON CONFLICT(user_id) DO NOTHING RETURNING user_id", (user["id"], Jsonb(state), ts))
                if not cur.fetchone():
                    return jsonify({"error": "Você já tem um perfil. Entre para continuar.", "code": "PROFILE_EXISTS"}), 409
            else:
                cur.execute("""
                  INSERT INTO rep_accounts (user_id,state,updated_at) VALUES (%s,%s,%s)
                  ON CONFLICT(user_id) DO UPDATE SET state=EXCLUDED.state, updated_at=EXCLUDED.updated_at
                """, (user["id"], Jsonb(state), ts))
            return jsonify({"ok": True, "state": state})
    except Exception as e:
        print("REP account storage error", str(e), flush=True)
        return jsonify({"error": "Não foi possível acessar seu perfil. Tente novamente.", "code": "STORAGE_UNAVAILABLE"}), 503
