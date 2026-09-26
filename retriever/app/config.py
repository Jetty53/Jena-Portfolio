from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://jena:jena@127.0.0.1:5432/jena?sslmode=disable"

    gemini_api_key: str = ""
    gemini_embed_model: str = "gemini-embedding-001"
    gemini_generate_model: str = "gemini-flash-latest"
    embed_dim: int = 768

    retrieve_token: str = "change-me"
    retrieve_top_k: int = 5
    retrieve_min_score: float = 0.25
    max_query_rewrite: int = 1
    history_turns: int = 6
    answer_max_tokens: int = 1024
    judge_max_tokens: int = 96
    rewrite_max_tokens: int = 80
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"


settings = Settings()
