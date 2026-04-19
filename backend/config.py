from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str
    n8n_base_url: str = "http://localhost:5678"
    google_project_id: str = ""
    gemini_api_key: str = ""
    debug: bool = True
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
