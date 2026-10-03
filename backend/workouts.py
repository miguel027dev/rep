import re
import unicodedata

TRAINING_METHOD = "TYVON Performance · progressão controlada"


def movement(key, name, group, equipment, tip, compound=False, requires=None):
    return {
        "id": key,
        "name": name,
        "group": group,
        "equipment": equipment,
        "tip": tip,
        "compound": compound,
        "requires": requires or [],
    }


LIB = {
    "barbell_bench": movement("barbell_bench", "Supino reto com barra", "Peitoral", "Barras", "Mantenha os pés firmes, escápulas apoiadas e controle a descida.", True, ["Barras", "Banco"]),
    "db_bench": movement("db_bench", "Supino reto com halteres", "Peitoral", "Halteres", "Desça com controle e mantenha os ombros estáveis.", True, ["Halteres", "Banco"]),
    "chest_machine": movement("chest_machine", "Supino na máquina", "Peitoral", "Máquinas", "Mantenha as escápulas apoiadas e controle a volta.", True),
    "pushup": movement("pushup", "Flexão de braços", "Peitoral", "Peso corporal", "Mantenha o corpo alinhado e use amplitude confortável.", True),
    "incline_barbell": movement("incline_barbell", "Supino inclinado com barra", "Peitoral", "Barras", "Use inclinação moderada e mantenha as escápulas apoiadas.", True, ["Barras", "Banco"]),
    "incline_db": movement("incline_db", "Supino inclinado com halteres", "Peitoral", "Halteres", "Controle a descida e evite elevar os ombros.", True, ["Halteres", "Banco"]),
    "incline_pushup": movement("incline_pushup", "Flexão inclinada", "Peitoral", "Peso corporal", "Use um apoio firme e mantenha o corpo alinhado.", True),
    "decline_pushup": movement("decline_pushup", "Flexão com pés elevados", "Peitoral", "Peso corporal", "Mantenha tronco firme e pare antes de perder a postura.", True),
    "cable_fly": movement("cable_fly", "Crucifixo no cabo", "Peitoral", "Cabos", "Aproxime as mãos sem perder o controle dos ombros."),
    "fly": movement("fly", "Crucifixo na máquina", "Peitoral", "Máquinas", "Feche os braços sem perder o controle dos ombros."),
    "pulldown": movement("pulldown", "Puxada aberta na polia", "Costas", "Cabos", "Puxe em direção ao peito sem usar impulso.", True),
    "neutral_pulldown": movement("neutral_pulldown", "Puxada neutra", "Costas", "Cabos", "Mantenha o tronco estável e conduza com os cotovelos.", True),
    "pulldown_machine": movement("pulldown_machine", "Puxada na máquina", "Costas", "Máquinas", "Controle a volta e mantenha o tronco estável.", True),
    "row_cable": movement("row_cable", "Remada baixa", "Costas", "Cabos", "Puxe com os cotovelos e evite balançar o tronco.", True),
    "row_machine": movement("row_machine", "Remada articulada", "Costas", "Máquinas", "Mantenha o peito estável e controle a volta.", True),
    "row_db": movement("row_db", "Remada unilateral com halter", "Costas", "Halteres", "Apoie o tronco e mantenha a coluna neutra.", True),
    "chest_supported_row": movement("chest_supported_row", "Remada apoiada com halteres", "Costas", "Halteres", "Apoie o peito no banco e puxe sem tirar o tronco do apoio.", True, ["Halteres", "Banco"]),
    "inverted_row": movement("inverted_row", "Remada invertida", "Costas", "Peso corporal", "Mantenha corpo alinhado e puxe o peito em direção ao apoio.", True),
    "back_bw": movement("back_bw", "Elevação de braços em W", "Costas", "Peso corporal", "Mova os braços com controle sem forçar a lombar."),
    "barbell_squat": movement("barbell_squat", "Agachamento com barra", "Quadríceps", "Barras", "Mantenha os pés firmes e a coluna estável durante a descida.", True),
    "legpress": movement("legpress", "Leg press", "Quadríceps", "Máquinas", "Mantenha a lombar apoiada e use amplitude confortável.", True),
    "hack_squat": movement("hack_squat", "Hack squat", "Quadríceps", "Máquinas", "Mantenha as costas apoiadas e controle a descida.", True),
    "goblet": movement("goblet", "Agachamento goblet", "Quadríceps", "Halteres", "Mantenha os pés firmes e o tronco estável.", True),
    "squat_bw": movement("squat_bw", "Agachamento livre", "Quadríceps", "Peso corporal", "Desça com controle até uma amplitude confortável.", True),
    "split_squat": movement("split_squat", "Agachamento dividido", "Quadríceps", "Peso corporal", "Mantenha equilíbrio e controle a descida."),
    "reverse_lunge": movement("reverse_lunge", "Afundo reverso", "Quadríceps", "Peso corporal", "Dê um passo para trás e mantenha o tronco estável."),
    "legext": movement("legext", "Cadeira extensora", "Quadríceps", "Máquinas", "Estenda os joelhos sem tirar o quadril do banco."),
    "barbell_rdl": movement("barbell_rdl", "Levantamento romeno com barra", "Posterior", "Barras", "Leve o quadril para trás mantendo a coluna neutra.", True),
    "rdl": movement("rdl", "Levantamento romeno com halteres", "Posterior", "Halteres", "Leve o quadril para trás mantendo a coluna neutra.", True),
    "single_leg_rdl": movement("single_leg_rdl", "RDL unilateral", "Posterior", "Peso corporal", "Controle o quadril e use apoio se necessário.", True),
    "legcurl": movement("legcurl", "Mesa flexora", "Posterior", "Máquinas", "Flexione os joelhos sem levantar o quadril."),
    "seated_legcurl": movement("seated_legcurl", "Flexora sentada", "Posterior", "Máquinas", "Mantenha o quadril apoiado e controle a volta."),
    "hip_thrust": movement("hip_thrust", "Hip thrust", "Glúteos", "Barras", "Mantenha o tronco estável e finalize sem hiperestender a lombar.", True, ["Barras", "Banco"]),
    "hipbridge": movement("hipbridge", "Ponte de glúteos", "Glúteos", "Peso corporal", "Eleve o quadril sem exagerar a curvatura lombar.", True),
    "single_leg_bridge": movement("single_leg_bridge", "Ponte unilateral", "Glúteos", "Peso corporal", "Mantenha a pelve estável durante o movimento.", True),
    "hip_machine": movement("hip_machine", "Extensão de quadril na máquina", "Glúteos", "Máquinas", "Controle o movimento e mantenha a pelve estável."),
    "shoulder_press": movement("shoulder_press", "Desenvolvimento na máquina", "Ombros", "Máquinas", "Controle a descida sem compensar com a lombar.", True),
    "db_press": movement("db_press", "Desenvolvimento com halteres", "Ombros", "Halteres", "Use amplitude confortável e tronco estável.", True),
    "pike_pushup": movement("pike_pushup", "Flexão pike", "Ombros", "Peso corporal", "Mantenha o tronco firme e use amplitude confortável.", True),
    "lateral": movement("lateral", "Elevação lateral", "Ombros", "Halteres", "Eleve com controle sem usar impulso."),
    "cable_lateral": movement("cable_lateral", "Elevação lateral no cabo", "Ombros", "Cabos", "Mantenha tensão contínua e evite impulso."),
    "rear_delt": movement("rear_delt", "Crucifixo inverso", "Ombros", "Máquinas", "Abra os braços mantendo o peito apoiado."),
    "face_pull": movement("face_pull", "Face pull", "Ombros", "Cabos", "Puxe em direção ao rosto mantendo os ombros estáveis."),
    "barbell_curl": movement("barbell_curl", "Rosca direta com barra", "Bíceps", "Barras", "Mantenha os cotovelos estáveis e evite balanço."),
    "curl_db": movement("curl_db", "Rosca alternada com halteres", "Bíceps", "Halteres", "Mantenha os cotovelos próximos ao corpo."),
    "incline_curl": movement("incline_curl", "Rosca inclinada com halteres", "Bíceps", "Halteres", "Mantenha o braço estável e controle a descida.", False, ["Halteres", "Banco"]),
    "curl_cable": movement("curl_cable", "Rosca na polia", "Bíceps", "Cabos", "Evite balançar o tronco."),
    "hammer_curl": movement("hammer_curl", "Rosca martelo", "Bíceps", "Halteres", "Mantenha punhos neutros e cotovelos estáveis."),
    "preacher_machine": movement("preacher_machine", "Rosca Scott na máquina", "Bíceps", "Máquinas", "Mantenha os braços apoiados durante toda a série."),
    "triceps": movement("triceps", "Tríceps na polia", "Tríceps", "Cabos", "Estenda os cotovelos sem mover os ombros."),
    "overhead_cable": movement("overhead_cable", "Tríceps acima da cabeça no cabo", "Tríceps", "Cabos", "Mantenha os cotovelos apontados para frente e controle a volta."),
    "triceps_db": movement("triceps_db", "Tríceps francês com halter", "Tríceps", "Halteres", "Mantenha os cotovelos estáveis e use carga confortável."),
    "close_pushup": movement("close_pushup", "Flexão fechada", "Tríceps", "Peso corporal", "Mantenha os cotovelos controlados e o corpo alinhado.", True),
    "calf_machine": movement("calf_machine", "Panturrilha na máquina", "Panturrilha", "Máquinas", "Use amplitude confortável e evite impulso."),
    "calf": movement("calf", "Elevação de panturrilha", "Panturrilha", "Peso corporal", "Suba e desça sem impulso e use apoio para equilíbrio."),
    "cable_crunch": movement("cable_crunch", "Abdominal no cabo", "Core", "Cabos", "Mova o tronco com controle e evite puxar com os braços."),
    "plank": movement("plank", "Prancha", "Core", "Peso corporal", "Respire normalmente e pare antes de perder o alinhamento."),
    "deadbug": movement("deadbug", "Dead bug", "Core", "Peso corporal", "Mantenha a lombar estável e mova braços e pernas devagar."),
}


def _has(profile, exercise):
    if exercise["equipment"] == "Peso corporal":
        return True
    equipment = set(profile.get("equipment") or [])
    required = exercise.get("requires") or []
    if required:
        return all(item in equipment for item in required)
    return exercise["equipment"] in equipment


def _pick(profile, *keys):
    exercises = [LIB[key] for key in keys]
    for exercise in exercises:
        if _has(profile, exercise):
            return exercise
    for exercise in exercises:
        if exercise["equipment"] == "Peso corporal":
            return exercise
    return exercises[-1]


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
        sets = 3 if exercise["compound"] else (2 if beginner else 3)
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


def _exercise_limit(profile, minor):
    minutes = max(30, min(90, int(profile.get("sessionMinutes") or 60)))
    if minor:
        return min(6, 5 if minutes <= 45 else 6)
    if minutes <= 35:
        return 5
    if minutes <= 45:
        return 6
    if minutes <= 60:
        return 8
    return 9


def _unique(exercises):
    out = []
    seen = set()
    for exercise in exercises:
        if exercise and exercise["id"] not in seen:
            seen.add(exercise["id"])
            out.append(exercise)
    return out


def _templates(profile):
    chest = _pick(profile, "barbell_bench", "db_bench", "chest_machine", "pushup")
    chest2 = _pick(profile, "incline_barbell", "incline_db", "chest_machine", "incline_pushup")
    chest3 = _pick(profile, "cable_fly", "fly", "decline_pushup", "pushup")
    row = _pick(profile, "row_cable", "row_machine", "chest_supported_row", "row_db", "inverted_row", "back_bw")
    row2 = _pick(profile, "chest_supported_row", "row_machine", "row_db", "row_cable", "inverted_row", "back_bw")
    pull = _pick(profile, "pulldown", "pulldown_machine", "neutral_pulldown", "inverted_row", "back_bw")
    pull2 = _pick(profile, "neutral_pulldown", "pulldown", "pulldown_machine", "inverted_row", "back_bw")
    squat = _pick(profile, "barbell_squat", "hack_squat", "legpress", "goblet", "squat_bw")
    quad = _pick(profile, "legext", "hack_squat", "goblet", "split_squat")
    unilateral = _pick(profile, "split_squat", "reverse_lunge")
    hinge = _pick(profile, "barbell_rdl", "rdl", "single_leg_rdl", "hipbridge")
    ham = _pick(profile, "legcurl", "seated_legcurl", "rdl", "single_leg_rdl")
    glute = _pick(profile, "hip_thrust", "hip_machine", "single_leg_bridge", "hipbridge")
    press = _pick(profile, "shoulder_press", "db_press", "pike_pushup")
    lateral = _pick(profile, "cable_lateral", "lateral", "pike_pushup")
    rear = _pick(profile, "rear_delt", "face_pull", "back_bw")
    curl = _pick(profile, "barbell_curl", "curl_cable", "curl_db")
    curl2 = _pick(profile, "incline_curl", "preacher_machine", "hammer_curl", "curl_db")
    tri = _pick(profile, "triceps", "triceps_db", "close_pushup")
    tri2 = _pick(profile, "overhead_cable", "triceps_db", "close_pushup")
    calf = _pick(profile, "calf_machine", "calf")
    core = _pick(profile, "cable_crunch", "plank")
    core2 = LIB["deadbug"]
    days = max(2, min(5, int(profile.get("days") or 3)))
    minor = isinstance(profile.get("age"), int) and profile["age"] < 18

    if minor:
        return [
            ("Corpo inteiro A", "Quadríceps · peito · costas · core", [squat, chest, row, hinge, core, calf]),
            ("Corpo inteiro B", "Posterior · ombros · costas · core", [hinge, press, pull, squat, core2, calf]),
            ("Corpo inteiro C", "Pernas · peito · costas · ombros", [squat, chest2, row, lateral, ham, core]),
        ][:min(days, 3)]

    if days == 2:
        return [
            ("Corpo inteiro A", "Peito · costas · pernas · ombros · braços", [squat, chest, row, hinge, press, curl, tri, core]),
            ("Corpo inteiro B", "Posterior · costas · peito · pernas · braços", [hinge, pull, chest2, quad, row2, curl2, tri2, calf]),
        ]
    if days == 3:
        return [
            ("Push", "Peito · ombros · tríceps", [chest, chest2, chest3, press, lateral, tri, tri2, core]),
            ("Pull", "Costas · bíceps · deltoides posteriores", [pull, row, row2, pull2, rear, curl, curl2, core2]),
            ("Pernas", "Quadríceps · posterior · glúteos · panturrilha", [squat, quad, hinge, ham, glute, unilateral, calf, core]),
        ]
    if days == 4:
        return [
            ("Superiores A", "Peito · costas · ombros · braços", [chest, chest2, row, pull, press, lateral, curl, tri]),
            ("Inferiores A", "Quadríceps · posterior · glúteos · core", [squat, quad, hinge, ham, glute, calf, core]),
            ("Superiores B", "Costas · peito · deltoides · braços", [pull2, row2, chest, chest3, rear, lateral, curl2, tri2]),
            ("Inferiores B", "Pernas · posterior · glúteos · core", [squat, unilateral, hinge, ham, glute, calf, core2]),
        ]
    return [
        ("Push", "Peito · ombros · tríceps", [chest, chest2, chest3, press, lateral, tri, tri2, core]),
        ("Pull", "Costas · bíceps · deltoides posteriores", [pull, row, row2, pull2, rear, curl, curl2, core2]),
        ("Pernas", "Quadríceps · posterior · glúteos", [squat, quad, hinge, ham, glute, unilateral, calf, core]),
        ("Superiores", "Peito · costas · ombros · braços", [chest, chest2, row, pull, press, lateral, curl, tri]),
        ("Inferiores", "Pernas · posterior · glúteos · core", [squat, quad, hinge, ham, glute, calf, core2]),
    ]


def make_plan(profile=None):
    profile = profile or {}
    minor = isinstance(profile.get("age"), int) and profile["age"] < 18
    restricted = bool(profile.get("limitations")) and profile.get("limitations") != "Nenhuma"
    limit = _exercise_limit(profile, minor)
    plan = []
    for idx, (name, focus, moves) in enumerate(_templates(profile)):
        exercises = [_prescribe(exercise, profile) for exercise in _unique(moves) if _has(profile, exercise) or exercise["equipment"] == "Peso corporal"][:limit]
        minutes = min(int(profile.get("sessionMinutes") or 60), max(35, len(exercises) * 7))
        plan.append({
            "id": idx,
            "name": name,
            "focus": focus,
            "kind": "strength",
            "method": "TYVON · técnica supervisionada" if minor else TRAINING_METHOD,
            "minutes": minutes,
            "intensity": "3–4 repetições de reserva" if minor else ("2–3 repetições de reserva" if profile.get("experience") == "Iniciante" else "1–3 repetições de reserva"),
            "recovery": "Distribua as sessões na semana e deixe os grupos musculares se recuperarem antes de repetir trabalho pesado.",
            "note": (
                "Dos 14 aos 17, priorize técnica, supervisão e cargas confortáveis; não use progressão automática de carga."
                if minor else
                "Você informou uma restrição. Valide exercícios e cargas com um profissional."
                if restricted else
                "Registre carga, repetições e RIR. O TYVON usa seu próprio histórico para sugerir o próximo passo."
            ),
            "progression": "Ajuste cargas com orientação profissional." if minor else "Quando você domina o topo da faixa com técnica estável e margem, o TYVON pode sugerir um pequeno aumento na próxima sessão.",
            "exercises": exercises,
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
        for item in raw["exercises"][:10]:
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
                "compound": item.get("compound") is True,
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
