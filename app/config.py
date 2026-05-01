# -*- coding: utf-8 -*-
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # Opción A — URL completa (tiene precedencia si está seteada)
    database_url: str = ""

    # Opción B — variables separadas (recomendado si la password tiene caracteres especiales)
    db_user: str = "postgres"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = ""

    n8n_base_url: str = "http://localhost:5678"
    n8n_webhook_mode: str = "test"
    n8n_webhook_secret: str = ""
    google_project_id: str = ""
    gemini_api_key: str = ""
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    api_key: str = ""
    app_env: str = "development"

    @property
    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        from urllib.parse import quote_plus
        password = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
