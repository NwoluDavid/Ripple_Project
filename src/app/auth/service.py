from pathlib import Path

from app.config import settings
from app.auth.schemas import EmailContent, EmailValidation
from app.utilities import send_email


def send_email_validation_email(data: EmailValidation) -> None:
    subject = f"{settings.PROJECT_NAME} - {data.subject}"
    server_host = settings.SERVER_HOST
    verify_route = settings.EMAILS_VERIFICATION_ROUTE
    link = f"{server_host}{verify_route}?token={data.token}"  # Todo change this
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "confirm_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=data.email,
        subject_template=subject,
        html_template=template_str,
        environment={"link": link},
    )


def send_web_contact_email(data: EmailContent) -> None:
    subject = f"{settings.PROJECT_NAME} - {data.subject}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "web_contact_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=settings.EMAILS_TO_EMAIL,
        subject_template=subject,
        html_template=template_str,
        environment={"content": data.content, "email": data.email},
    )


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_magic_login_email(email_to: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"Your {project_name} magic login"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "magic_login.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}?magic={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "valid_minutes": int(settings.ACCESS_TOKEN_EXPIRE_SECONDS / 60),
            "link": link,
        },
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    server_host = settings.SERVER_HOST
    reset_route = settings.EMAILS_RESET_ROUTE
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    # link = f"{server_host}/reset-password?token={token}"
    link = f"{server_host}{reset_route}?token={token}"  # Todo change this
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": int(settings.ACCESS_TOKEN_EXPIRE_SECONDS / 60),
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )
