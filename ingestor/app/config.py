from pathlib import Path
import tempfile

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://jena:jena@localhost:5432/jena"

    gemini_api_key: str = ""
    gemini_embed_model: str = "gemini-embedding-001"
    gemini_vision_model: str = "gemini-flash-latest"
    embed_dim: int = 768

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "rag-portfolio"
    r2_endpoint: str = ""
    r2_prefix_in_progress: str = "in-progress"
    r2_prefix_succeeded: str = "succeeded"
    r2_prefix_failed: str = "failed"

    ingest_token: str = "change-me"
    max_file_bytes: int = 10 * 1024 * 1024
    max_files_per_request: int = 10
    tmp_dir: str = Field(default_factory=lambda: str(Path(tempfile.gettempdir()) / "jena-ingest"))

    chunker_version: str = "semantic-v1"
    chunk_max_tokens: int = 512
    chunk_min_tokens: int = 64
    semantic_sim_threshold: float = 0.55
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"


settings = Settings()
