import os
import secrets
from typing import List

from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
    SALT_KEY: str = os.getenv("SALT_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:5000", "http://localhost:8000"]
    PROJECT_NAME: str = "Auto Parts Management System"

    DATABASE_HOST: str = os.getenv("DATABASE_HOST")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT")
    DATABASE_USER: str = os.getenv("DATABASE_USER")
    DATABASE_PASS: str = os.getenv("DATABASE_PASS")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")

    DATABASE_URL: str = (f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:"
                         f"{DATABASE_PORT}/{DATABASE_NAME}")
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True


settings = Settings()
