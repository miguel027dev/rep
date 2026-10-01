from backend.workouts import make_plan, select_workout_cards, sanitize_workout_cards

PROFILE = {"name":"Miguel","goal":"Ganhar massa muscular","experience":"Avançado","equipment":["Halteres","Banco","Cabos","Máquinas"],"days":4,"limitations":"Nenhuma"}

def test_plan_matches_expected_shape():
    plan = make_plan(PROFILE)
    assert len(plan) == 4
    assert plan[0]["name"] == "Ombros e tríceps"
    assert all(e["sets"] == 1 and e["restSeconds"] >= 90 and e["warmupSets"] >= 1 for w in plan for e in w["exercises"])
    assert all(w["intensity"] == "1–2 repetições de reserva" for w in plan)

def test_minor_plan_is_conservative():
    plan = make_plan({**PROFILE, "age": 14})
    assert all(w["intensity"] == "3–4 repetições de reserva" for w in plan if w["kind"] == "strength")
    assert all("supervisionada" in w["method"] for w in plan if w["kind"] == "strength")

def test_card_selection():
    assert select_workout_cards("Qual treino faço hoje?", PROFILE, 2)[0]["id"] == 2
    assert select_workout_cards("Monte um treino de costas", PROFILE)[0]["name"] == "Costas"
    assert select_workout_cards("Como escolher a carga?", PROFILE) == []

def test_card_sanitization_bounds():
    plan = make_plan(PROFILE)
    unsafe = [{**plan[0], "exercises": [{**plan[0]["exercises"][0], "sets": 999, "restSeconds": 0, "name": "a" * 1000}]}]
    card = sanitize_workout_cards(unsafe)[0]
    assert card["exercises"][0]["sets"] == 6
    assert card["exercises"][0]["restSeconds"] == 90
    assert len(card["exercises"][0]["name"]) == 100
