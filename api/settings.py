from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    REDIS_URL: str

    MAIL_USER: str
    MAIL_HOST: str
    MAIL_PORT: int = 465
    MAIL_PASS: str
    MAIL_SSL_TLS: bool = True
    MAIL_STARTTLS: bool = False
    MAIL_FROM: str
    MAIL_FROM_NAME: str

    class Config:
        env_file = ".env"

setting = Setting()