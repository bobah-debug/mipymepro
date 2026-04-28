from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Mi PyME PRO"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql://pyme:pyme1234@localhost:5432/pymedb"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    SECRET_KEY: str = "cambia-esta-clave-secreta-en-produccion-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CORS_ORIGINS: list[str] = ["*"]

    FRONTEND_BUILD_DIR: Optional[str] = None

    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"

    SII_AMBIENTE: str = "certificacion"
    SII_RUT_EMISOR: str = ""
    SII_RAZON_SOCIAL: str = ""
    SII_CERT_PATH: str = ""
    SII_CERT_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
