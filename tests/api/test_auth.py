from tests.conftest import login

API = "/api/v1/auth"


def test_register_login_me(client):
    body = {
        "name": "Ana Ruiz",
        "email": "Ana@Correo.com",
        "password": "secreta123",
        "role": "PATIENT",
        "accept_terms": True,
    }
    r = client.post(f"{API}/register", json=body)
    assert r.status_code == 201
    assert r.json()["user"]["email"] == "ana@correo.com"
    assert "insumap_rt" in r.cookies
    assert client.post(f"{API}/register", json=body).json()["error"]["code"] == "EMAIL_IN_USE"
    headers = login(client, "ana@correo.com", "secreta123")
    assert client.get(f"{API}/me", headers=headers).json()["role"] == "PATIENT"


def test_register_requires_terms_and_digit(client):
    base = {"name": "Ana", "email": "a@b.co", "password": "secreta123", "role": "PATIENT"}
    assert (
        client.post(f"{API}/register", json={**base, "accept_terms": False}).json()["error"]["code"]
        == "TERMS_NOT_ACCEPTED"
    )
    r = client.post(f"{API}/register", json={**base, "accept_terms": True, "password": "sinnumeros"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_credentials_and_rate_limit(client):
    for _ in range(5):
        r = client.post(f"{API}/login", json={"email": "paciente@demo.insumap", "password": "mala1234"})
        assert r.json()["error"]["code"] == "INVALID_CREDENTIALS"
    r = client.post(f"{API}/login", json={"email": "paciente@demo.insumap", "password": "Insumap123"})
    assert r.status_code == 429


def test_swagger_form_login(client):
    r = client.post(f"{API}/token", data={"username": "paciente@demo.insumap", "password": "Insumap123"})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"


def test_refresh_rotation_and_logout(client):
    login(client, "paciente@demo.insumap")
    old = client.cookies.get("insumap_rt")
    r = client.post(f"{API}/refresh")
    assert r.status_code == 200
    assert client.cookies.get("insumap_rt") != old
    client.cookies.set("insumap_rt", old, path="/api/v1/auth")
    assert client.post(f"{API}/refresh").status_code == 401  # old token was revoked
    login(client, "paciente@demo.insumap")
    assert client.post(f"{API}/logout").status_code == 204


def test_expired_access_token(client, frozen):
    headers = login(client, "paciente@demo.insumap")
    frozen.advance(minutes=601)
    r = client.get(f"{API}/me", headers=headers)
    assert r.status_code == 401 and r.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_password_reset_flow(client):
    from app.services import email_service

    assert client.post(f"{API}/forgot-password", json={"email": "nadie@x.co"}).status_code == 202
    client.post(f"{API}/forgot-password", json={"email": "paciente@demo.insumap"})
    body = email_service.outbox[-1].get_content()
    token = body.split("token=")[1].split()[0]
    r = client.post(f"{API}/reset-password", json={"token": token, "new_password": "nueva1234"})
    assert r.status_code == 200
    assert client.post(f"{API}/reset-password", json={"token": token, "new_password": "otra12345"}).status_code == 400
    login(client, "paciente@demo.insumap", "nueva1234")


def test_protected_route_without_token(client):
    r = client.get("/api/v1/map")
    assert r.status_code == 401 and r.json()["error"]["code"] == "NOT_AUTHENTICATED"
