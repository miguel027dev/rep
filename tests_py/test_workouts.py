from backend.workouts import make_plan, sanitize_workout_cards, select_workout_cards

PROFILE={"name":"Miguel","age":25,"height":175,"weight":78,"goal":"Ganhar massa muscular","experience":"Avançado","equipment":["Halteres","Banco","Cabos","Máquinas"],"days":4,"sessionMinutes":60,"limitations":"Nenhuma"}


def test_adult_plan_is_complete():
    for days in (2,3,4,5):
        plan=make_plan({**PROFILE,"days":days})
        assert len(plan)==days
        assert all(len(w["exercises"])>=6 for w in plan)
        assert all(2<=e["sets"]<=3 for w in plan for e in w["exercises"])


def test_session_duration_caps_exercises():
    plan=make_plan({**PROFILE,"days":3,"sessionMinutes":35})
    assert all(len(w["exercises"])<=5 for w in plan)


def test_minor_plan_is_conservative():
    plan=make_plan({**PROFILE,"age":14,"days":5})
    assert len(plan)<=3
    assert all(w["intensity"]=="3–4 repetições de reserva" for w in plan)
    assert all(len(w["exercises"])<=6 for w in plan)
    assert all(e["sets"]==2 and e["targetRir"]==4 for w in plan for e in w["exercises"])


def test_card_selection():
    assert select_workout_cards("Qual treino faço hoje?",PROFILE,2)[0]["id"]==2
    assert select_workout_cards("Quero o treino B",PROFILE)[0]["id"]==1
    assert select_workout_cards("Como escolher a carga?",PROFILE)==[]


def test_card_sanitization_bounds():
    plan=make_plan(PROFILE)
    unsafe=[{**plan[0],"exercises":[{**plan[0]["exercises"][0],"sets":999,"restSeconds":0,"name":"a"*1000}]}]
    card=sanitize_workout_cards(unsafe)[0]
    assert card["exercises"][0]["sets"]==6
    assert card["exercises"][0]["restSeconds"]==90
    assert len(card["exercises"][0]["name"])==100
