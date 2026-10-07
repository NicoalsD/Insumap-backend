import httpx

API = "/api/v1/assistant/messages"


def test_degraded_mode_without_ai_service(client, patient):
    r = client.post(API, json={"message": "¿Dónde me inyecto ahora?"}, headers=patient)
    assert r.status_code == 200
    data = r.json()
    assert data["degraded"] is True and data["source"] == "template"
    assert data["referenced_microzones"][0] in data["reply"]
    assert [m["role"] for m in client.get(API, headers=patient).json()] == ["USER", "ASSISTANT"]


def test_dose_guardrail(client, patient):
    data = client.post(API, json={"message": "¿Cuántas unidades me pongo hoy?"}, headers=patient).json()
    assert data["source"] == "guardrail" and "médico" in data["reply"]


def test_rate_limit(client, patient):
    for _ in range(20):
        client.post(API, json={"message": "hola"}, headers=patient)
    assert client.post(API, json={"message": "hola"}, headers=patient).status_code == 429


def test_ai_service_with_delegated_token(client, patient, monkeypatch):
    from app.core.config import get_settings

    captured = {}

    def fake_post(url, json, headers, timeout):
        captured.update(json)
        # The AI service reads data with the delegated token...
        tool = client.get("/api/v1/suggestions", headers={"Authorization": f"Bearer {json['delegated_token']}"})
        assert tool.status_code == 200
        top = tool.json()["suggestions"][0]["microzone_id"]
        return httpx.Response(
            200,
            json={"reply": f"Usa {top}", "referenced_microzones": [top], "model": "deepseek-chat"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(get_settings(), "ai_service_url", "http://ai.local")
    monkeypatch.setattr(httpx, "post", fake_post)
    data = client.post(API, json={"message": "¿Dónde me toca?"}, headers=patient).json()
    assert data["degraded"] is False and data["source"] == "deepseek-chat"
    # ...but cannot write with it.
    delegated = {"Authorization": f"Bearer {captured['delegated_token']}"}
    assert client.post("/api/v1/injections", json={"microzone_id": "ABD-I-1-1"}, headers=delegated).status_code == 403
