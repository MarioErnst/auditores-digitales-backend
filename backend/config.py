from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    n8n_base_url: str = "http://localhost:5678"
    google_project_id: str = ""
    gemini_api_key: str = ""
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
