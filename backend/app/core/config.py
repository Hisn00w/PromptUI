from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    app_name: str = 'PromptUI API'
    app_env: str = 'development'
    api_prefix: str = '/api/v1'

    database_url: str = 'postgresql+asyncpg://promptui:promptui@db:5432/promptui'
    database_url_sync: str = 'postgresql+psycopg2://promptui:promptui@db:5432/promptui'

    redis_url: str = 'redis://redis:6379/0'

    jwt_secret_key: str = 'change-this-in-production'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    cors_origins: List[str] = ['http://localhost:5173', 'http://127.0.0.1:5173']

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith('['):
                import json

                return json.loads(value)
            return [item.strip() for item in value.split(',') if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
