import re
import unicodedata

TRAINING_METHOD = "TYVON Performance · progressão controlada"


def movement(key, name, group, equipment, tip, compound=False):
    return {"id": key, "name": name, "group": group, "equipment": equipment, "tip": tip, "compound": compound}


LIB = {
    "chest_machine": movement("chest_machine", "Supino na máquina", "Peitoral", "Máquinas", "Mantenha as escápulas apoiadas e controle a descida.", True),
    "db_bench": movement("db_bench", "Supino com halteres", "Peitoral", "Halteres", "Desça com controle e mantenha os ombros estáveis.", True),
    "pushup": movement("pushup", "Flexão inclinada", "Peitoral", "Peso corporal", "Use um apoio firme e mantenha o corpo alinhado.", True),
    "incline_db": movement("incline_db", "Supino inclinado com halteres", "Peitoral", "Halteres", "Use amplitude confortável e controle o retorno.", True),
    "fly": movement("fly", "Crucifixo na máquina", "Peitoral", "Máquinas", "Feche os braços sem perder o controle dos ombros."),
    "row_cable": movement("row_cable", "Remada baixa", "Costas", "Cabos", "Puxe com os cotovelos e evite balançar o tronco.", True),
    "row_machine": movement("row_machine", "Remada na máquina", "Costas", "Máquinas", "Mantenha o peito estável e controle a volta.", True),
    "row_db": movement("row_db", "Remada unilateral", "Costas", "Halteres", "Apoie o tronco e mantenha a coluna neutra.", True),
    "pulldown": movement("pulldown", "Puxada na polia", "Costas", "Cabos", "Puxe em direção ao peito sem usar impulso.", True),
    "pulldown_machine": movement("pulldown_machine", "Puxada na máquina", "Costas", "Máquinas", "Controle a volta e mantenha o tronco estável.", True),
    "back_bw": movement("back_bw", "Elevação de braços em W", "Costas", "Peso corporal", "Mova os braços com controle sem forçar a lombar."),
    "legpress": movement("legpress", "Leg press", "Quadríceps", "Máquinas", "Mantenha a lombar apoiada e use amplitude confortável.", True),
    "goblet": movement("goblet", "Agachamento goblet", "Quadríceps", "Halteres", "Mantenha os pés firmes e o tronco estável.", True),
    "squat_bw": movement("squat_bw", "Agachamento livre", "Quadríceps", "Peso corporal", "Desça com controle até uma amplitude confortável.", True),
    "legext": movement("legext", "Cadeira extensora", "Quadríceps", "Máquinas", "Estenda os joelhos sem tirar o quadril do banco."),
    "rdl": movement("rdl", "Levantamento romeno", "Posterior", "Halteres", "Leve o quadril para trás mantendo a coluna neutra.", True),
    "legcurl": movement("legcurl", "Mesa flexora", "Posterior", "Máquinas", "Flexione os joelhos sem levantar o quadril."),
    "hipbridge": movement("hipbridge", "Ponte de glúteos", "Glúteos", "Peso corporal", "Eleve o quadril sem exagerar a curvatura lombar.", True),
    "hip_machine": movement("hip_machine", "Extensão de quadril na máquina", "Glúteos", "Máquinas", "Controle o movimento e mantenha a pelve estável."),
    "shoulder_press": movement("shoulder_press", "Desenvolvimento na máquina", "Ombros", "Máquinas", "Controle a descida sem compensar com a lombar.", True),
    "db_press": movement("db_press", "Desenvolvimento com halteres", "Ombros", "Halteres", "Use amplitude confortável e tronco estável.", True),
    "wall_press": movement("wall_press", "Flexão na parede", "Ombros", "Peso corporal", "Mantenha o corpo alinhado e use ritmo controlado.", True),
    "lateral": movement("lateral", "Elevação lateral", "Ombros", "Halteres", "Eleve com controle sem usar impulso."),
    "rear_delt": movement("rear_delt", "Crucifixo inverso", "Ombros", "Máquinas", "Abra os braços mantendo o peito apoiado."),
    "curl_db": movement("curl_db", "Rosca com halteres", "Bíceps", "Halteres", "Mantenha os cotovelos estáveis."),
    "curl_cable": movement("curl_cable", "Rosca na polia", "Bíceps", "Cabos", "Evite balançar o tronco."),
    "triceps": movement("triceps", "Tríceps na polia", "Tríceps", "Cabos", "Estenda os cotovelos sem mover os ombros."),
    "triceps_db": movement("triceps_db", "Tríceps com halter", "Tríceps", "Halteres", "Mantenha o cotovelo estável e use carga confortável."),
    "calf": movement("calf", "Elevação de panturrilha", "Panturrilha", "Peso corporal", "Suba e desça sem impulso e use apoio para equilíbrio."),
    "plank": movement("plank", "Prancha", "Core", "Peso corporal", "Respire normalmente e pare antes de perder o alinhamento."),
    "deadbug": movement("deadbug", "Dead bug", "Core", "Peso corporal", "Mantenha a lombar estável e mova braços e pernas devagar."),
}


def _has(profile, equipment):
    return equipment == "Peso corporal" or equipment in (profile.get("equipment") or [])


def _pick(profile, *keys):
    for key in keys:
        if _has(profile, LIB[key]["equipment"]):
            return LIB[key]
    return LIB[keys[-1]]


def _clean(text):
    return unicodedata.normalize("NFD", str(text or "")).encode("ascii", "ignore").decode().lower()


def _prescribe(exercise, profile):
    age = profile.get("age")
    minor = isinstance(age, int) and age < 18
    experience = profile.get("experience") or "Iniciante"
    goal = profile.get("goal") or "Criar uma rotina"
    beginner = experience == "Iniciante"
    if minor:
        sets = 2
        reps = "8–12" if exercise["compound"] else "10–15"
        rir = 4
        rest = 120 if exercise["compound"] else 75
    else:
        sets = 2 if beginner and not exercise["compound"] else 3
        if goal == "Ganhar massa muscular":
            reps = "6–10" if exercise["compound"] else "10–15"
        elif goal == "Melhorar condicionamento":
            reps = "10–15"
        else:
            reps = "8–12" if exercise["compound"] else "10–15"
        rir = 3 if beginner else 2
        rest = 90 if goal == "Melhorar condicionamento" else (150 if exercise["compound"] else 90)
    if exercise["id"] == "plank":
        reps = "20–40 s"
    return {
        **exercise,
        "sets": sets,
        "warmupSets": 2 if exercise["compound"] else 1,
        "reps": reps,
        "targetRir": rir,
        "restSeconds": rest,
    }


def _templates(profile):
    chest = _pick(profile, "chest_machine", "db_bench", "pushup")
    chest2 = _pick(profile, "incline_db", "fly", "pushup")
    row = _pick(profile, "row_cable", "row_machine", "row_db", "back_bw")
    pull = _pick(profile, "pulldown", "pulldown_machine", "row_cable", "row_machine", "row_db", "back_bw")
    squat = _pick(profile, "legpress", "goblet", "squat_bw")
    quad = _pick(profile, "legext", "goblet", "squat_bw")
    hinge = _pick(profile, "rdl", "hipbridge")
    ham = _pick(profile, "legcurl", "rdl", "hipbridge")
    glute = _pick(profile, "hip_machine", "hipbridge")
    press = _pick(profile, "shoulder_press", "db_press", "wall_press")
    lateral = _pick(profile, "lateral", "rear_delt", "wall_press")
    rear = _pick(profile, "rear_delt", "lateral", "back_bw")
    curl = _pick(profile, "curl_cable", "curl_db", "plank")
    tri = _pick(profile, "triceps", "triceps_db", "pushup")
    calf = LIB["calf"]
    core = LIB["plank"]
    core2 = LIB["deadbug"]
    days = max(2, min(5, int(profile.get("days") or 3)))
    minor = isinstance(profile.get("age"), int) and profile["age"] < 18

    if minor:
        return [
            ("Corpo inteiro A", "Quadríceps · peito · costas · core", [squat, chest, row, hinge, core]),
            ("Corpo inteiro B", "Posterior · ombros · costas · core", [hinge, press, pull, squat, core2]),
            ("Corpo inteiro C", "Pernas · peito · costas · ombros", [squat, chest2, row, lateral, core]),
        ][:min(days, 3)]

    if days == 2:
        return [
            ("Corpo inteiro A", "Peito · costas · quadríceps · ombros", [squat, chest, row, hinge, lateral, core]),
            ("Corpo inteiro B", "Posterior · costas · peito · braços", [hinge, pull, chest2, quad, curl, tri]),
        ]
    if days == 3:
        return [
            ("Corpo inteiro A", "Peito · costas · quadríceps", [chest, row, squat, lateral, curl, core]),
            ("Corpo inteiro B", "Posterior · ombros · costas", [hinge, press, pull, quad, tri, calf]),
            ("Corpo inteiro C", "Pernas · peito · costas · braços", [squat, chest2, row, ham, curl, tri]),
        ]
    if days == 4:
        return [
            ("Superiores A", "Peito · costas · ombros · braços", [chest, row, press, lateral, curl, tri]),
            ("Inferiores A", "Quadríceps · posterior · glúteos · core", [squat, hinge, quad, ham, calf, core]),
            ("Superiores B", "Costas · peito · deltoides · braços", [pull, chest2, row, rear, curl, tri]),
            ("Inferiores B", "Pernas · posterior · glúteos · core", [squat, ham, hinge, glute, calf, core2]),
        ]
    return [
        ("Push", "Peito · ombros · tríceps", [chest, chest2, press, lateral, tri, core]),
        ("Pull", "Costas · bíceps · deltoides posteriores", [pull, row, rear, curl, core, calf]),
        ("Pernas", "Quadríceps · posterior · glúteos", [squat, quad, hinge, ham, glute, calf]),
        ("Superiores", "Peito · costas · ombros · braços", [chest, row, press, lateral, curl, tri]),
        ("Inferiores", "Pernas · posterior · core", [squat, hinge, quad, ham, calf, core2]),
    ]


def make_plan(profile=None):
    profile = profile or {}
    minor = isinstance(profile.get("age"), int) and profile["age"] < 18
    restricted = bool(profile.get("limitations")) and profile.get("limitations") != "Nenhuma"
    plan = []
    for idx, (name, focus, exercises) in enumerate(_templates(profile)):
        prescribed = [_prescribe(exercise, profile) for exercise in exercises]
        plan.append({
            "id": idx,
            "name": name,
            "focus": focus,
            "kind": "strength",
            "method": "TYVON · técnica supervisionada" if minor else TRAINING_METHOD,
            "minutes": 45 if minor else (55 if len(prescribed) >= 6 else 45),
            "intensity": "3–4 repetições de reserva" if minor else ("2–3 repetições de reserva" if profile.get("experience") == "Iniciante" else "1–3 repetições de reserva"),
            "recovery": "Distribua as sessões na semana e deixe os grupos musculares se recuperarem antes de treiná-los pesado novamente.",
            "note": (
                "Dos 13 aos 17, priorize técnica, supervisão e cargas confortáveis; não treine até a falha."
                if minor else
                "Você informou uma restrição. Valide exercícios e cargas com um profissional."
                if restricted else
                "Registre cargas e repetições. Aumente a dificuldade apenas quando a execução estiver estável."
            ),
            "progression": "Ajuste cargas com orientação profissional." if minor else "Ao atingir o topo da faixa com boa técnica e margem, use um pequeno aumento de carga na próxima sessão.",
            "exercises": prescribed,
        })
    return plan


def select_workout_cards(text, profile, next_workout_id=0):
    t = _clean(text)
    if not profile.get("goal") or not profile.get("experience") or not profile.get("days") or not profile.get("equipment"):
        return []
    if re.search(r"\b(dor|dores|lesao|lesoes|machucado|tontura|desmaio)\b", t):
        return []
    if not re.search(r"\b(treino|treinos|plano|rotina|ficha|exercicios)\b", t):
        return []
    plan = make_plan(profile)
    letter = re.search(r"\btreino\s+([a-e])\b", t)
    if letter:
        return [plan[min(ord(letter.group(1)) - 97, len(plan) - 1)]]
    if re.search(r"\b(hoje|agora|proximo|proxima)\b", t):
        return [plan[min(max(0, int(next_workout_id)), len(plan) - 1)]]
    for workout in plan:
        if _clean(workout["name"]).split()[0] in t and len(plan) > 2:
            return [workout]
    return plan


def workout_summary(workouts, profile=None):
    profile = profile or {}
    first = str(profile.get("name") or "").split(" ")[0]
    prefix = f"{first}, " if first and first != "Você" else ""
    if len(workouts) == 1:
        return f"{prefix}separei {workouts[0]['name'].lower()} para hoje. São {len(workouts[0]['exercises'])} exercícios com aquecimento, séries principais e descanso definidos."
    return f"{prefix}seu plano tem {len(workouts)} sessões completas. Abra os cards para ver exercícios, séries, repetições e descanso de cada dia."


def _bounded_text(value, limit):
    return str(value or "").strip()[:limit]


def sanitize_workout_cards(cards):
    if not isinstance(cards, list):
        return []
    out = []
    for idx, raw in enumerate(cards[:5]):
        if not isinstance(raw, dict) or not isinstance(raw.get("exercises"), list) or not raw.get("name"):
            continue
        exercises = []
        for item in raw["exercises"][:8]:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            try:
                sets = min(6, max(1, int(item.get("sets") or 1)))
                rest = min(300, max(45, int(item.get("restSeconds") or 90)))
                warmup = min(4, max(0, int(item.get("warmupSets") or 0)))
                target_rir = min(5, max(0, int(item.get("targetRir") if item.get("targetRir") is not None else 2)))
            except (TypeError, ValueError):
                continue
            exercises.append({
                "id": _bounded_text(item.get("id"), 80),
                "name": _bounded_text(item.get("name"), 100),
                "group": _bounded_text(item.get("group"), 60),
                "equipment": _bounded_text(item.get("equipment"), 40),
                "tip": _bounded_text(item.get("tip"), 300),
                "sets": sets,
                "warmupSets": warmup,
                "restSeconds": rest,
                "reps": _bounded_text(item.get("reps"), 30),
                "targetRir": target_rir,
            })
        if not exercises:
            continue
        out.append({
            "id": min(4, max(0, int(raw.get("id") if isinstance(raw.get("id"), int) else idx))),
            "name": _bounded_text(raw.get("name"), 120),
            "focus": _bounded_text(raw.get("focus"), 160),
            "kind": "strength",
            "method": _bounded_text(raw.get("method"), 120),
            "minutes": min(120, max(20, int(raw.get("minutes") or 50))),
            "intensity": _bounded_text(raw.get("intensity"), 120),
            "recovery": _bounded_text(raw.get("recovery"), 300),
            "note": _bounded_text(raw.get("note"), 400),
            "progression": _bounded_text(raw.get("progression"), 400),
            "exercises": exercises,
        })
    return out
