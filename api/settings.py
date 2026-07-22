from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    DB_URL: str
    JWT_SECRET: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str

    MAIL_USER: str
    MAIL_HOST: str 
    MAIL_PORT: int = 465
    MAIL_PASS: str
    MAIL_SSL_TLS: bool = True
    MAIL_STARTTLS: bool = False
    MAIL_FROM: str
    MAIL_FROM_NAME: str

    CLOUDINARY_NAME: str
    CLOUDINARY_SECRET: str
    CLOUDINARY_KEY: str
    IMAGE_FOLDER: str = "16vmart"

    STRIPE_SECRET: str
    STRIPE_HOOK_SECRET: str

    APP_URL: str

    class Config:
        env_file = ".env"

setting = Setting()