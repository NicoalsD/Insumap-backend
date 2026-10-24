import pytest


@pytest.mark.parametrize(
    "origin",
    [
        "https://insumap-frontend.vercel.app",
        "https://insumap-frontend-nicolas-bd0c.vercel.app",
        "https://insumap-frontend-5prjeehs1-nicolas-bd0c.vercel.app",
    ],
)
def test_cors_allows_project_vercel_origins(client, origin):
    r = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == origin
    assert r.headers["access-control-allow-credentials"] == "true"


def test_cors_rejects_unknown_origin(client):
    r = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "https://insumap-frontend.evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.status_code == 400
    assert "access-control-allow-origin" not in r.headers
