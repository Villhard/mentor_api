from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config(BaseSettings):
    # Основные настройки Django
    SECRET_KEY: str
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "*"

    # Настройки базы данных
    DB_ENGINE: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    # Настройки языка и времени
    LANGUAGE_CODE: str = "ru-ru"
    TIME_ZONE: str = "Europe/Moscow"

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    @property
    def ALLOWED_HOSTS_LIST(self):
        if self.ALLOWED_HOSTS == "*":
            return ["*"]
        return self.ALLOWED_HOSTS.split(",")


config = Config()
