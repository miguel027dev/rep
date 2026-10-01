import re
import unicodedata

TRAINING_METHOD = "HIT · inspirado em Dorian Yates"


def movement(name, group, equipment, tip, compound=False):
    return {"name": name, "group": group, "equipment": equipment, "tip": tip, "compound": compound}


def make_plan(p=None):
    p = p or {}
    eq = p.get("equipment") if isinstance(p.get("equipment"), list) and p.get("equipment") else ["Peso corporal"]
    has = lambda e: e in eq
    age = p.get("age")
    minor = isinstance(age, int) and age < 18
    beginner = minor or p.get("experience") not in ["Intermediário", "Avançado"]
    restricted = bool(p.get("limitations")) and p.get("limitations") != "Nenhuma"
    bodyweight = not any(has(e) for e in ["Halteres", "Máquinas", "Cabos", "Barras"])
    days = min(5, max(2, int(p.get("days") or 3)))

    chest = movement("Supino na máquina", "Peitoral", "Máquinas", "Desça com controle e mantenha as escápulas apoiadas.", True) if has("Máquinas") else (movement("Supino com halteres" if has("Banco") else "Supino com halteres no chão", "Peitoral", "Halteres", "Controle a descida. Pare antes de perder a posição dos ombros.", True) if has("Halteres") else movement("Flexão inclinada", "Peitoral", "Peso corporal", "Use uma parede ou apoio firme. Mantenha o corpo alinhado.", True))
    row = movement("Remada baixa", "Costas", "Cabos", "Puxe com os cotovelos, sem jogar o tronco para trás.", True) if has("Cabos") else (movement("Remada unilateral", "Costas", "Halteres", "Apoie a mão e mantenha a coluna neutra.", True) if has("Halteres") else (movement("Remada na máquina", "Costas", "Máquinas", "Controle a volta e mantenha o peito apoiado.", True) if has("Máquinas") else (movement("Remada com barra", "Costas", "Barras", "Use carga que permita manter a coluna neutra.", True) if has("Barras") else movement("Elevação de braços em W", "Costas", "Peso corporal", "Deitado de barriga para baixo, mova os braços sem forçar a lombar."))))
    pulldown = movement("Puxada na polia", "Costas", "Cabos", "Puxe em direção à parte alta do peito, sem balanço.", True) if has("Cabos") else (movement("Puxada na máquina", "Costas", "Máquinas", "Mantenha o tronco estável e controle a volta.", True) if has("Máquinas") else None)
    squat = movement("Leg press", "Pernas", "Máquinas", "Mantenha a lombar apoiada e use uma amplitude confortável.", True) if has("Máquinas") else (movement("Agachamento goblet", "Pernas", "Halteres", "Segure o halter junto ao peito e mantenha os pés apoiados.", True) if has("Halteres") else movement("Agachamento livre", "Pernas", "Peso corporal", "Desça com controle até uma amplitude confortável.", True))
    hip = movement("Levantamento romeno", "Posterior", "Halteres", "Leve o quadril para trás, mantendo a coluna neutra.", True) if has("Halteres") else movement("Ponte de glúteos", "Glúteos", "Peso corporal", "Eleve o quadril sem exagerar a curvatura da lombar.")
    shoulder = movement("Elevação lateral", "Ombros", "Halteres", "Use carga leve e eleve até a linha dos ombros.") if has("Halteres") else movement("Flexão na parede", "Ombros", "Peso corporal", "Mantenha o corpo alinhado e use um ritmo controlado.", True)
    press = movement("Desenvolvimento na máquina", "Ombros", "Máquinas", "Evite arquear a lombar e controle a descida.", True) if has("Máquinas") else (movement("Desenvolvimento com halteres", "Ombros", "Halteres", "Use uma amplitude confortável, sem compensar com a lombar.", True) if has("Halteres") else shoulder)
    curl = movement("Rosca com halteres", "Bíceps", "Halteres", "Mantenha os cotovelos junto ao corpo, sem impulso.") if has("Halteres") else (movement("Rosca na polia", "Bíceps", "Cabos", "Mantenha o tronco estável durante toda a repetição.") if has("Cabos") else None)
    triceps = movement("Tríceps na polia", "Tríceps", "Cabos", "Estenda os cotovelos sem mover os ombros.") if has("Cabos") else (movement("Extensão de tríceps deitado", "Tríceps", "Halteres", "Use carga leve e mantenha os cotovelos estáveis.") if has("Halteres") else movement("Flexão na parede com mãos próximas", "Tríceps", "Peso corporal", "Aproxime as mãos apenas até uma posição confortável.", True))
    legcurl = movement("Mesa flexora", "Posterior", "Máquinas", "Flexione os joelhos sem levantar o quadril.") if has("Máquinas") else movement("Afundo com apoio", "Pernas", "Halteres" if has("Halteres") else "Peso corporal", "Use apoio firme e respeite a amplitude confortável.", True)
    calf = movement("Elevação de panturrilha", "Panturrilha", "Peso corporal", "Suba e desça sem impulso, com apoio para equilíbrio.")
    core = movement("Prancha", "Core", "Peso corporal", "Respire normalmente e pare antes de perder o alinhamento.")

    if beginner or bodyweight or days == 2:
        sessions = [
            ["Corpo inteiro A", "Pernas · peito · costas", [squat, chest, row, hip, core]],
            ["Corpo inteiro B", "Posterior · ombros · costas", [hip, press, row, calf, core]],
            ["Corpo inteiro C", "Pernas · peito · core", [squat, chest, row, curl or shoulder, core]],
            ["Corpo inteiro D", "Posterior · costas · ombros", [hip, row, shoulder, calf, core]],
        ]
    elif days == 3:
        sessions = [
            ["Peito, ombros e tríceps", "Empurrar · superiores", [chest, press, shoulder, triceps]],
            ["Costas e bíceps", "Puxar · superiores", [x for x in [pulldown, row, curl, core] if x]],
            ["Pernas e core", "Pernas · glúteos · posterior", [squat, hip, legcurl, calf, core]],
        ]
    else:
        sessions = [
            ["Ombros e tríceps", "Ombros · tríceps", [press, shoulder, triceps]],
            ["Costas", "Costas · posterior", [x for x in [pulldown, row, hip, core] if x]],
            ["Peito e bíceps", "Peitoral · bíceps", [x for x in [chest, curl, core] if x]],
            ["Pernas", "Quadríceps · posterior · panturrilha", [squat, legcurl, calf, core]],
        ]
    if not minor and (beginner or bodyweight) and days >= 4:
        sessions = [
            ["Superiores A", "Peito · costas · ombros", [chest, row, shoulder, curl or core]],
            ["Inferiores A", "Pernas · posterior · core", [squat, hip, calf, core]],
            ["Superiores B", "Ombros · costas · tríceps", [press, row, triceps, core]],
            ["Inferiores B", "Pernas · posterior · panturrilha", [squat, legcurl, calf, core]],
        ]

    resistance = []
    for idx, (name, focus, moves) in enumerate(sessions[:min(days, 3 if minor else 4)]):
        exercises = []
        for e in moves:
            reps = "20–30 s" if e["name"] == "Prancha" else ("12–15" if e["group"] == "Panturrilha" else ("8–12" if beginner else (("6–10" if e["compound"] else "10–12") if p.get("goal") == "Ganhar massa muscular" else "10–15")))
            exercises.append({
                "name": e["name"], "group": e["group"], "equipment": e["equipment"], "tip": e["tip"],
                "sets": 2 if beginner else 1, "warmupSets": 2 if e["compound"] else 1,
                "restSeconds": 120 if e["compound"] and beginner else (150 if e["compound"] else 90), "reps": reps,
            })
        resistance.append({
            "id": idx, "name": name, "focus": focus, "kind": "strength",
            "method": "BASE · técnica supervisionada" if minor else TRAINING_METHOD,
            "minutes": 40 if beginner else 35,
            "intensity": "3–4 repetições de reserva" if minor else ("2–3 repetições de reserva" if beginner or restricted else "1–2 repetições de reserva"),
            "recovery": "Deixe pelo menos 48 horas entre estas sessões de corpo inteiro." if (beginner or bodyweight) and days <= 3 else "Distribua as sessões na semana e dê 48–72 horas de recuperação ao mesmo grupo muscular.",
            "note": "Dos 13 aos 17, treine com acompanhamento de um responsável e profissional. Priorize técnica, sem falha ou testes máximos." if minor else ("Você informou uma restrição. Valide estes exercícios com um profissional antes de começar." if restricted else ("Primeiro domine o movimento. As séries principais terminam com 2–3 repetições de reserva." if beginner else "Uma série principal por exercício, com execução controlada. Sem repetições forçadas ou ajuda para ultrapassar a falha.")),
            "progression": "Ajuste cargas apenas com seu professor, quando o movimento estiver confortável e estável." if minor else "Quando alcançar o topo da faixa com boa técnica em todas as séries, considere um pequeno aumento de carga na próxima sessão.",
            "exercises": exercises,
        })
    if days == 5 or (minor and days >= 4):
        resistance.append({
            "id": len(resistance), "name": "Recuperação ativa", "focus": "Mobilidade · movimento leve", "kind": "recovery",
            "method": "RECUPERAÇÃO · REP", "minutes": 25, "intensity": "Ritmo confortável",
            "recovery": "Recuperar também faz parte do plano.",
            "note": "Este quinto dia é leve. Ele não acrescenta outra sessão intensa de musculação.",
            "progression": "Mantenha um ritmo em que consiga conversar sem dificuldade.",
            "exercises": [
                {"name": "Caminhada leve", "group": "Condicionamento", "equipment": "Peso corporal", "tip": "Caminhe em um ritmo confortável.", "sets": 1, "warmupSets": 0, "restSeconds": 60, "reps": "15 min"},
                {"name": "Mobilidade de quadril", "group": "Mobilidade", "equipment": "Peso corporal", "tip": "Movimente sem dor e sem forçar a amplitude.", "sets": 1, "warmupSets": 0, "restSeconds": 60, "reps": "3 min"},
                {"name": "Mobilidade de ombros", "group": "Mobilidade", "equipment": "Peso corporal", "tip": "Faça movimentos leves e confortáveis.", "sets": 1, "warmupSets": 0, "restSeconds": 60, "reps": "3 min"},
            ],
        })
    return resistance


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFD", str(text or "")) if unicodedata.category(c) != "Mn").lower()


def select_workout_cards(text, p, next_workout_id=0):
    t = normalized(text)
    if not p.get("goal") or not p.get("experience") or not p.get("days") or not p.get("equipment"):
        return []
    if re.search(r"\b(dor|dores|lesao|lesoes|machucado|tontura)\b", t):
        return []
    explicit = re.search(r"\b(monte|monta|montar|crie|cria|criar|gere|gera|gerar|mostre|mostra|mostrar|prepare|preparar|recomende|recomenda|sugira|sugere|organize|organiza|quero|preciso|mande|manda|mandar|envie|enviar|passa|passe|da|de|ver|fazer|comecar)\b.*\b(treino|treinos|plano|rotina|ficha|exercicios)\b", t)
    request = bool(explicit or re.fullmatch(r"\s*(treino|treinos|plano)\s*", t) or re.search(r"\b(quero|preciso)\b.*\btreinar\b", t) or re.search(r"\b(qual|que) treino\b|\b(meu|meus|minha) (treino|treinos|plano|rotina|ficha)\b|\btreinar\b.*\b(hoje|agora)\b|\btreino\b.*\b(hoje|peito|costas|pernas|ombros|biceps|triceps|completo|dorian|hit|a|b|c|d)\b", t))
    if not request:
        return []
    if not explicit and re.search(r"\b(carga|descans|descanso|recuperacao|tecnica|por que|porque)\b", t):
        return []
    plan = make_plan(p)
    letter = re.search(r"\btreino ([a-e])\b", t)
    if letter:
        return [plan[min(ord(letter.group(1)) - 97, len(plan) - 1)]]
    muscles = [("peito", "Peitoral"), ("costas", "Costas"), ("pernas", "Pernas"), ("ombros", "Ombros"), ("biceps", "Bíceps"), ("triceps", "Tríceps")]
    muscle = next(((word, group) for word, group in muscles if re.search(rf"\b{word}\b", t)), None)
    if muscle:
        word, group = muscle
        scored = []
        for w in plan:
            score = sum(1 for e in w["exercises"] if e["group"] == group or (word == "pernas" and e["group"] in ["Pernas", "Posterior", "Panturrilha"]))
            scored.append((score, w))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [scored[0][1]] if scored and scored[0][0] else []
    if re.search(r"\b(hoje|agora|proximo|proxima)\b", t):
        return [plan[min(max(0, int(next_workout_id)), len(plan) - 1)]]
    return plan


def bounded_text(v, max_len):
    return v.strip()[:max_len] if isinstance(v, str) else ""


def sanitize_workout_cards(value):
    if not isinstance(value, list):
        return []
    result = []
    for w in value[:5]:
        if not isinstance(w, dict) or not isinstance(w.get("exercises"), list) or not w["exercises"] or not isinstance(w.get("name"), str):
            continue
        exercises = []
        for e in w["exercises"][:8]:
            if not isinstance(e, dict) or not isinstance(e.get("name"), str):
                continue
            exercises.append({
                "name": bounded_text(e.get("name"), 100), "group": bounded_text(e.get("group"), 60),
                "equipment": bounded_text(e.get("equipment"), 60), "tip": bounded_text(e.get("tip"), 300),
                "sets": min(6, max(1, round(float(e.get("sets") or 1)))),
                "warmupSets": min(3, max(0, round(float(e.get("warmupSets") or 0)))),
                "restSeconds": min(300, max(30, round(float(e.get("restSeconds") or 90)))),
                "reps": bounded_text(e.get("reps"), 40),
                "id": bounded_text(e.get("id"), 80),
                "targetRir": min(5, max(0, float(e.get("targetRir")))) if isinstance(e.get("targetRir"), (int,float)) else None,
                "suggestedLoad": min(500, max(0, float(e.get("suggestedLoad")))) if isinstance(e.get("suggestedLoad"), (int,float)) else None,
                "progressionReason": bounded_text(e.get("progressionReason"), 300),
            })
        if exercises:
            result.append({
                "id": w.get("id") if isinstance(w.get("id"), int) and 0 <= w["id"] < 5 else 0,
                "name": bounded_text(w.get("name"), 100), "focus": bounded_text(w.get("focus"), 120),
                "kind": "recovery" if w.get("kind") == "recovery" else "strength", "method": bounded_text(w.get("method"), 80),
                "minutes": min(120, max(10, float(w.get("minutes") or 35))), "intensity": bounded_text(w.get("intensity"), 100),
                "recovery": bounded_text(w.get("recovery"), 250), "note": bounded_text(w.get("note"), 350),
                "progression": bounded_text(w.get("progression"), 300), "exercises": exercises,
            })
    return result


def workout_summary(workouts, profile=None):
    profile = profile or {}
    age = profile.get("age")
    minor = isinstance(age, int) and 13 <= age < 18
    name = str(profile.get("name") or "").strip().split(" ")[0]
    prefix = f"{name}, " if name and name != "Você" else ""
    if len(workouts) == 1:
        w = workouts[0]
        if w.get("kind") == "recovery":
            return f"{prefix}hoje é dia de recuperar. Seu card reúne movimento leve e mobilidade, em um ritmo confortável.\n\nAbra cada exercício para ver os detalhes e comece quando estiver pronto."
        tail = "Treine com acompanhamento de um responsável e profissional." if minor else "As séries e os intervalos estão no card."
        return f"{prefix}vamos de {w['name'].lower()} hoje. São {len(w['exercises'])} exercícios, em cerca de {w['minutes']} minutos.\n\nAqueça com calma e mantenha {w['intensity'].lower()}, sempre com boa técnica. {tail}"
    tail = "Priorize técnica e treine com acompanhamento de um responsável e profissional." if minor else "Vamos construir constância, uma sessão de cada vez."
    return f"{prefix}seu plano está nos {len(workouts)} cards abaixo, organizado para a sua rotina.\n\nEscolha um treino para ver os exercícios, aquecimentos e intervalos. {tail}"
