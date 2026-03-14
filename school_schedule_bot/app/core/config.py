from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'School Schedule Bot'
    api_host: str = '0.0.0.0'
    api_port: int = 8000
    bot_token: str = Field(default='CHANGE_ME', alias='BOT_TOKEN')
    database_url: str = Field(default='sqlite:///./school_schedule.db', alias='DATABASE_URL')
    log_level: str = 'INFO'


@lru_cache
def get_settings() -> Settings:
    return Settings()
