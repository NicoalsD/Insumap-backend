"""Outgoing email. Without SMTP settings, messages are logged (local development)."""

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

log = logging.getLogger("insumap.email")
outbox: list[EmailMessage] = []  # last messages, useful for tests and local debugging


def send(to: str, subject: str, body: str) -> None:
    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    outbox.append(msg)
    del outbox[:-20]
    if not s.smtp_host:
        log.warning("SMTP not configured; email to %s:\n%s", to, body)
        return
    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=10) as smtp:
        smtp.starttls()
        if s.smtp_user:
            smtp.login(s.smtp_user, s.smtp_password)
        smtp.send_message(msg)
