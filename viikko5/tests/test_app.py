from unittest.mock import patch
from app.main import app


def test_health_endpoint():
    client = app.test_client()
    with patch.dict("os.environ", {"COMMIT_SHA": "abc1234test"}):
        res = client.get("/viikko5/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["commit_sha"] == "abc1234test"


def test_index_loads_empty_session():
    client = app.test_client()
    with patch("app.main.fetch_history", return_value=[]):
        res = client.get("/viikko5/")
        assert res.status_code == 200
        assert "Paikallinen LLM Chat" in res.get_data(as_text=True)


def test_chat_endpoint_success():
    client = app.test_client()
    mock_history = [{"role": "user", "content": "Moi!"}]
    with (
        patch("app.main.save_message") as mock_save,
        patch("app.main.fetch_history", return_value=mock_history),
        patch("app.main.query_ollama", return_value="Terve! Miten voin auttaa?"),
    ):
        res = client.post("/viikko5/api/chat", json={"message": "Moi!"})
        assert res.status_code == 200
        assert res.get_json()["reply"] == "Terve! Miten voin auttaa?"
        assert mock_save.call_count == 2


def test_chat_endpoint_empty_message():
    client = app.test_client()
    res = client.post("/viikko5/api/chat", json={"message": "   "})
    assert res.status_code == 400
