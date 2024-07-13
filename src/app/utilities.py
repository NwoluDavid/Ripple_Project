import logging
from typing import Any, Dict

import emails
from emails.template import JinjaTemplate

from app.config import settings


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}

    if settings.SMTP_TLS:
        # https://python-emails.readthedocs.io/en/latest/
        smtp_options["tls"] = False
    elif settings.SMTP_SSL:
        smtp_options["ssl"] = True

    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    # Add common template environment elements
    environment["server_host"] = settings.SERVER_HOST
    environment["server_name"] = settings.SERVER_NAME
    environment["server_bot"] = settings.SERVER_BOT
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")
    print(environment, smtp_options, "email sent well")
