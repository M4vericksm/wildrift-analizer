from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da Fase 0 — ver docs/decisions/0002-fase-0-sem-fila-sem-gpu.md.

    Sem Redis/Celery: o processamento roda em BackgroundTasks no próprio
    processo da API. Storage é um diretório local, não R2 (ADR 0003 é Fase 1+).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://wildrift:wildrift@localhost:5432/wildrift"
    storage_dir: str = "./var/videos"
    max_upload_mb: int = 600

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    groq_api_key: str = ""


settings = Settings()
