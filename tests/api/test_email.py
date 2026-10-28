def test_smtp_uses_starttls_and_credentials(monkeypatch):
    from app.core.config import get_settings
    from app.services import email_service

    settings = get_settings()
    monkeypatch.setattr(settings, "smtp_host", "smtp.gmail.com")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_user", "demo@gmail.com")
    monkeypatch.setattr(settings, "smtp_password", "app-password")
    monkeypatch.setattr(settings, "smtp_from", "Insumap <demo@gmail.com>")

    calls: dict[str, object] = {}

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            calls["connection"] = (host, port, timeout)

        def __enter__(self) -> "FakeSMTP":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def starttls(self) -> None:
            calls["tls"] = True

        def login(self, user: str, password: str) -> None:
            calls["login"] = (user, password)

        def send_message(self, message: object) -> None:
            calls["to"] = message["To"]  # type: ignore[index]

    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

    email_service.send("destino@correo.com", "Asunto", "Cuerpo")

    assert calls["connection"] == ("smtp.gmail.com", 587, 10)
    assert calls["tls"] is True
    assert calls["login"] == ("demo@gmail.com", "app-password")
    assert calls["to"] == "destino@correo.com"
