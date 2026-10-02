GOALS = {"Ganhar massa muscular", "Melhorar condicionamento", "Perder gordura", "Criar uma rotina"}
EXPERIENCE = {"Iniciante", "Intermediário", "Avançado"}
EQUIPMENT = {"Halteres", "Barras", "Máquinas", "Cabos", "Banco", "Peso corporal"}
PRIVACY_KINDS = {"access", "correction", "deletion", "portability", "consent", "sharing", "automated", "other"}


def clean_text(value, max_len):
    return value.strip()[:max_len] if isinstance(value, str) else ""


def normalize_profile(raw, email=""):
    if not isinstance(raw, dict):
        raise ValueError("Perfil inválido.")
    equipment = raw.get("equipment") if isinstance(raw.get("equipment"), list) else []
    equipment = [clean_text(x, 40) for x in equipment[:8]]
    if any(x not in EQUIPMENT for x in equipment):
        raise ValueError("Equipamento inválido.")
    age = raw.get("age")
    if age is not None and (not isinstance(age, int) or isinstance(age, bool) or not 13 <= age <= 100):
        raise ValueError("O TYVON está disponível a partir de 13 anos.")
    weight = raw.get("weight")
    if weight is not None and (not isinstance(weight, (int, float)) or isinstance(weight, bool) or not 30 <= weight <= 350):
        raise ValueError("Peso inválido.")
    days = raw.get("days")
    if days is not None and (not isinstance(days, int) or isinstance(days, bool) or not 2 <= days <= 5):
        raise ValueError("Frequência inválida.")
    goal = clean_text(raw.get("goal"), 120)
    experience = clean_text(raw.get("experience"), 40)
    limitations = clean_text(raw.get("limitations"), 500) or "Nenhuma"
    if goal and goal not in GOALS:
        raise ValueError("Objetivo inválido.")
    if experience and experience not in EXPERIENCE:
        raise ValueError("Experiência inválida.")
    if age is not None and age < 18 and goal == "Perder gordura":
        goal = "Criar uma rotina"
    out = {
        "email": email,
        "name": clean_text(raw.get("name"), 40) or "Você",
        "age": age,
        "weight": weight,
        "goal": goal,
        "experience": experience,
        "equipment": equipment,
        "days": days,
        "limitations": limitations,
        "complete": raw.get("complete") is True,
        "theme": "essential",
        "experienceVersion": "v1",
    }
    if out["complete"] and not all([out["age"], out["weight"], out["goal"], out["experience"], out["equipment"], out["days"], out["limitations"]]):
        raise ValueError("Conclua as perguntas do perfil.")
    return out
