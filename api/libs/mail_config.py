from pathlib import Path

from fastapi_mail import ConnectionConfig
from settings import setting

conf = ConnectionConfig(
    MAIL_SERVER=setting.MAIL_HOST,
    MAIL_USERNAME=setting.MAIL_USER,
    MAIL_PASSWORD=setting.MAIL_PASS,
    MAIL_PORT=setting.MAIL_PORT,
    MAIL_SSL_TLS=setting.MAIL_SSL_TLS,
    MAIL_STARTTLS=setting.MAIL_STARTTLS,
    MAIL_FROM=setting.MAIL_FROM,
    MAIL_FROM_NAME=setting.MAIL_FROM_NAME,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent / 'email_templates'
)