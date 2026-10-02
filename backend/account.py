import hashlib
import json
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from psycopg.types.json import Jsonb

from .auth import resolve_identity
from .db import get_db
from .logging_utils import log_event
from .request_security import require_csrf
from .validation import clean_text, normalize_profile
from .workouts import sanitize_workout_cards

account_bp = Blueprint("account", __name__)


class RevisionConflict(RuntimeError):
    def __init__(self, revision):
        self.revision = revision
        super().__init__("state revision conflict")


def _json_hash(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _as_json(value, fallback):
    if value is None:
        return fallback
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return fallback
    return value


def validate_account_state(raw, email):
    if not isinstance(raw, dict) or not isinstance(raw.get("profile"), dict):
        raise ValueError("Perfil inválido.")
    step = raw.get("step")
    if not isinstance(step, int) or isinstance(step, bool) or not 0 <= step <= 8:
        raise ValueError("Etapa inválida.")
    profile = normalize_profile(raw["profile"], email)

    messages = []
    source_messages = raw.get("messages")
    if isinstance(source_messages, list):
        for item in source_messages[-200:]:
            if not isinstance(item, dict):
                continue
            text = clean_text(item.get("text"), 16000)
            if not text:
                continue
            message = {
                "role": "user" if item.get("role") == "user" else "ai",
                "text": text,
            }
            if item.get("plan") is True:
                message["plan"] = True
            if item.get("preview") is True:
                message["preview"] = True
            if item.get("role") != "user" and isinstance(item.get("workouts"), list):
                cards = sanitize_workout_cards(item["workouts"])
                if cards:
                    message["workouts"] = cards
            messages.append(message)

    logs = []
    source_logs = raw.get("logs")
    if isinstance(source_logs, list):
        for item in source_logs[-500:]:
            if not isinstance(item, dict):
                continue
            log_id = clean_text(item.get("id"), 80)
            if not log_id:
                continue
            weights = {}
            if isinstance(item.get("weights"), dict):
                for key, value in list(item["weights"].items())[:160]:
                    weights[clean_text(str(key), 40)] = clean_text(str(value), 24)
            set_logs = []
            if isinstance(item.get("setLogs"), list):
                for raw_set in item["setLogs"][:220]:
                    if not isinstance(raw_set, dict):
                        continue
                    try:
                        reps = min(100, max(0, int(float(raw_set.get("reps") or 0))))
                        weight = min(500, max(0, float(raw_set.get("weight") or 0)))
                        rir = min(5, max(0, float(raw_set.get("rir") if raw_set.get("rir") is not None else 2)))
                        target_rir = min(5, max(0, float(raw_set.get("targetRir") if raw_set.get("targetRir") is not None else rir)))
                        set_index = min(20, max(1, int(float(raw_set.get("setIndex") or 1))))
                    except (TypeError, ValueError):
                        continue
                    set_logs.append({
                        "exerciseId": clean_text(raw_set.get("exerciseId"), 80),
                        "exerciseName": clean_text(raw_set.get("exerciseName"), 100),
                        "group": clean_text(raw_set.get("group"), 60),
                        "setIndex": set_index,
                        "weight": weight,
                        "reps": reps,
                        "rir": rir,
                        "targetRir": target_rir,
                        "completed": raw_set.get("completed") is True,
                    })
            feedback = {}
            if isinstance(item.get("feedback"), dict):
                effort = item["feedback"].get("effort")
                if isinstance(effort, (int, float)) and not isinstance(effort, bool) and 1 <= effort <= 5:
                    feedback["effort"] = int(effort)
            try:
                minutes = min(600, max(1, float(item.get("minutes") or 1)))
                sets = min(300, max(0, float(item.get("sets") or 0)))
            except (TypeError, ValueError):
                continue
            logs.append({
                "id": log_id,
                "name": clean_text(item.get("name"), 120) or "Treino",
                "date": clean_text(item.get("date"), 40) or datetime.now(timezone.utc).isoformat(),
                "minutes": minutes,
                "sets": sets,
                "weights": weights,
                "setLogs": set_logs,
                "feedback": feedback,
                "engine": "tyvon",
            })
    return {"profile": profile, "messages": messages, "logs": logs, "step": step}


def load_state(conn, user_id, email):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM tyvon_profiles WHERE user_id=%s", (user_id,))
        profile_row = cur.fetchone()
        if not profile_row:
            return None, 0
        cur.execute("SELECT step,revision FROM tyvon_account_meta WHERE user_id=%s", (user_id,))
        meta = cur.fetchone() or {"step": 0, "revision": 1}
        cur.execute("""
          SELECT position,role,text,plan,preview,workouts
          FROM tyvon_messages
          WHERE user_id=%s
          ORDER BY position ASC
        """, (user_id,))
        message_rows = cur.fetchall()
        cur.execute("""
          SELECT id,name,occurred_at,minutes,sets,weights,feedback
          FROM tyvon_workout_logs
          WHERE user_id=%s
          ORDER BY occurred_at ASC
        """, (user_id,))
        log_rows = cur.fetchall()
        log_ids = [row["id"] for row in log_rows]
        sets_by_log = {log_id: [] for log_id in log_ids}
        if log_ids:
            cur.execute("""
              SELECT workout_id,exercise_id,exercise_name,muscle_group,set_index,weight,reps,rir,target_rir,completed
              FROM tyvon_workout_sets
              WHERE workout_id=ANY(%s)
              ORDER BY workout_id,set_index,id
            """, (log_ids,))
            for row in cur.fetchall():
                sets_by_log.setdefault(row["workout_id"], []).append({
                    "exerciseId": row["exercise_id"],
                    "exerciseName": row["exercise_name"],
                    "group": row["muscle_group"],
                    "setIndex": row["set_index"],
                    "weight": float(row["weight"] or 0),
                    "reps": int(row["reps"] or 0),
                    "rir": float(row["rir"] or 0),
                    "targetRir": float(row["target_rir"] or 0),
                    "completed": bool(row["completed"]),
                })

    profile = {
        "email": email,
        "name": profile_row["name"],
        "age": profile_row["age"],
        "weight": float(profile_row["weight"]) if profile_row["weight"] is not None else None,
        "goal": profile_row["goal"] or "",
        "experience": profile_row["experience"] or "",
        "equipment": _as_json(profile_row["equipment"], []),
        "days": profile_row["days"],
        "limitations": profile_row["limitations"] or "Nenhuma",
        "complete": bool(profile_row["complete"]),
    }
    messages = []
    for row in message_rows:
        item = {"role": row["role"], "text": row["text"]}
        if row["plan"]:
            item["plan"] = True
        if row["preview"]:
            item["preview"] = True
        workouts = _as_json(row["workouts"], None)
        if workouts:
            item["workouts"] = workouts
        messages.append(item)

    logs = []
    for row in log_rows:
        logs.append({
            "id": row["id"],
            "name": row["name"],
            "date": row["occurred_at"].isoformat(),
            "minutes": float(row["minutes"]),
            "sets": float(row["sets"]),
            "weights": _as_json(row["weights"], {}),
            "setLogs": sets_by_log.get(row["id"], []),
            "feedback": _as_json(row["feedback"], {}),
            "engine": "tyvon",
        })
    return {"profile": profile, "messages": messages, "logs": logs, "step": int(meta["step"])}, int(meta["revision"])


def persist_state(conn, user_id, email, raw, expected_revision=None, migration_mode=False):
    state = validate_account_state(raw, email)
    messages_hash = _json_hash(state["messages"])
    logs_hash = _json_hash(state["logs"])
    with conn.cursor() as cur:
        cur.execute("SELECT revision,messages_hash,logs_hash FROM tyvon_account_meta WHERE user_id=%s FOR UPDATE", (user_id,))
        meta = cur.fetchone()
        current_revision = int(meta["revision"]) if meta else 0
        if expected_revision is not None and meta and int(expected_revision) != current_revision:
            raise RevisionConflict(current_revision)

        p = state["profile"]
        cur.execute("""
          INSERT INTO tyvon_profiles(user_id,email,name,age,weight,goal,experience,equipment,days,limitations,theme,complete,updated_at)
          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'essential',%s,NOW())
          ON CONFLICT(user_id) DO UPDATE SET
            email=EXCLUDED.email,name=EXCLUDED.name,age=EXCLUDED.age,weight=EXCLUDED.weight,
            goal=EXCLUDED.goal,experience=EXCLUDED.experience,equipment=EXCLUDED.equipment,
            days=EXCLUDED.days,limitations=EXCLUDED.limitations,theme='essential',
            complete=EXCLUDED.complete,updated_at=NOW()
        """, (
            user_id, email, p["name"], p["age"], p["weight"], p["goal"], p["experience"],
            Jsonb(p["equipment"]), p["days"], p["limitations"], p["complete"],
        ))

        if not meta or meta["messages_hash"] != messages_hash:
            cur.execute("DELETE FROM tyvon_messages WHERE user_id=%s", (user_id,))
            for position, message in enumerate(state["messages"]):
                cur.execute("""
                  INSERT INTO tyvon_messages(user_id,position,role,text,plan,preview,style_picker,workouts)
                  VALUES(%s,%s,%s,%s,%s,%s,FALSE,%s)
                """, (
                    user_id, position, message["role"], message["text"],
                    bool(message.get("plan")), bool(message.get("preview")),
                    Jsonb(message.get("workouts")) if message.get("workouts") else None,
                ))

        if not meta or meta["logs_hash"] != logs_hash:
            cur.execute("DELETE FROM tyvon_workout_logs WHERE user_id=%s", (user_id,))
            for log in state["logs"]:
                try:
                    occurred_at = datetime.fromisoformat(str(log["date"]).replace("Z", "+00:00"))
                except ValueError:
                    occurred_at = datetime.now(timezone.utc)
                if occurred_at.tzinfo is None:
                    occurred_at = occurred_at.replace(tzinfo=timezone.utc)
                cur.execute("""
                  INSERT INTO tyvon_workout_logs(id,user_id,name,occurred_at,minutes,sets,weights,feedback,engine)
                  VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'tyvon')
                """, (
                    log["id"], user_id, log["name"], occurred_at, log["minutes"], log["sets"],
                    Jsonb(log["weights"]), Jsonb(log["feedback"]),
                ))
                for set_log in log["setLogs"]:
                    cur.execute("""
                      INSERT INTO tyvon_workout_sets(
                        workout_id,exercise_id,exercise_name,muscle_group,set_index,weight,reps,rir,target_rir,completed
                      ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        log["id"], set_log["exerciseId"], set_log["exerciseName"], set_log["group"],
                        set_log["setIndex"], set_log["weight"], set_log["reps"], set_log["rir"],
                        set_log["targetRir"], set_log["completed"],
                    ))

        next_revision = max(1, current_revision + (0 if migration_mode and current_revision else 1))
        if not meta:
            next_revision = 1
        cur.execute("""
          INSERT INTO tyvon_account_meta(user_id,step,revision,messages_hash,logs_hash,updated_at)
          VALUES(%s,%s,%s,%s,%s,NOW())
          ON CONFLICT(user_id) DO UPDATE SET
            step=EXCLUDED.step,revision=%s,messages_hash=EXCLUDED.messages_hash,
            logs_hash=EXCLUDED.logs_hash,updated_at=NOW()
        """, (user_id, state["step"], next_revision, messages_hash, logs_hash, next_revision))
    return state, next_revision


@account_bp.route("/api/account", methods=["GET", "POST", "PUT", "DELETE"])
def account():
    user = resolve_identity()
    if not user:
        return jsonify({"error": "Entre com sua conta para continuar.", "code": "SIGN_IN_REQUIRED"}), 401
    if request.method != "GET":
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error

    with get_db() as conn:
        if request.method == "GET":
            state, revision = load_state(conn, user["id"], user["email"])
            return jsonify({
                "user": {
                    **user,
                    "emailVerified": bool(user.get("email_verified")),
                },
                "state": state,
                "revision": revision,
            })

        if request.method == "DELETE":
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tyvon_profiles WHERE user_id=%s", (user["id"],))
                cur.execute("DELETE FROM tyvon_account_meta WHERE user_id=%s", (user["id"],))
                cur.execute("DELETE FROM tyvon_messages WHERE user_id=%s", (user["id"],))
                cur.execute("DELETE FROM tyvon_workout_logs WHERE user_id=%s", (user["id"],))
                cur.execute("DELETE FROM tyvon_accounts WHERE user_id=%s", (user["id"],))
            return jsonify({"ok": True})

        if "application/json" not in (request.content_type or ""):
            return jsonify({"error": "Envie os dados em JSON."}), 415
        raw_bytes = request.get_data(cache=False)
        if len(raw_bytes) > 1_000_000:
            return jsonify({"error": "Seu histórico está muito grande."}), 413
        try:
            raw = json.loads(raw_bytes)
        except json.JSONDecodeError:
            return jsonify({"error": "Dados inválidos."}), 400

        if request.method == "POST":
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM tyvon_profiles WHERE user_id=%s", (user["id"],))
                if cur.fetchone():
                    return jsonify({"error": "Você já tem um perfil. Entre para continuar.", "code": "PROFILE_EXISTS"}), 409
            expected_revision = None
        else:
            header = request.headers.get("If-Match")
            try:
                expected_revision = int(header) if header is not None and header != "" else None
            except ValueError:
                return jsonify({"error": "Versão de estado inválida."}), 400

        try:
            state, revision = persist_state(conn, user["id"], user["email"], raw, expected_revision=expected_revision)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except RevisionConflict as exc:
            log_event("warning", "account_revision_conflict", user_id=user["id"], expected=expected_revision, current=exc.revision)
            return jsonify({
                "error": "Seus dados foram atualizados em outra aba ou dispositivo. Recarregue antes de salvar novamente.",
                "code": "STATE_CONFLICT",
                "revision": exc.revision,
            }), 409
        return jsonify({"ok": True, "state": state, "revision": revision})
