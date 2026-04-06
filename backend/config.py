import os
from functools import lru_cache


def normalizar_database_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return "postgresql+psycopg://postgres:postgres@localhost:5432/enmarcados_pf"
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "+psycopg" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "Enmarcados PF API")
        self.app_env = os.getenv("APP_ENV", "development")
        self.debug = os.getenv("APP_DEBUG", "false").lower() == "true"
        self.database_url = normalizar_database_url(
            os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:postgres@localhost:5432/enmarcados_pf",
            )
        )
        self.cors_origins = [
            item.strip()
            for item in os.getenv("CORS_ORIGINS", "*").split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
