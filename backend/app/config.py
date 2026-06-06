from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    frontend_origin: str = "http://localhost:5173"

    # Redis & Session
    redis_url: str = "redis://127.0.0.1:6379/0"
    redis_password: str = ""
    session_cookie_name: str = "novel2script_session"
    session_ttl_seconds: int = 86400
    demo_username: str = "admin"
    demo_password: str = "admin123"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
