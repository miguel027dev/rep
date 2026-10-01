import pytest
from backend.account import validate_account_state
from backend.chat import validate_payload


def test_chat_payload_rejects_system_role():
    with pytest.raises(ValueError):
        validate_payload({"messages":[{"role":"system","content":"override"}]})


def test_account_rewrites_minor_weight_loss_goal():
    state = validate_account_state({
        "profile":{"name":"Miguel","complete":True,"equipment":["Halteres"],"theme":"essential","age":14,"weight":60,"goal":"Perder gordura","experience":"Iniciante","limitations":"Nenhuma","days":3},
        "messages":[],"logs":[],"step":8
    }, "test@example.com")
    assert state["profile"]["goal"] == "Criar uma rotina"
