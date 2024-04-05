import logging
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import app

DEFAULT_ENV_FILE = ".env"
DEFAULT_API_ENV = "local"
DEFAULT_API_VERSION = "0.0.0"
APITALLY_CLIENT_ID = "52e18f0a-c986-495d-8a12-be2e139da490"


def is_testing() -> bool:
    return os.getenv("TESTING", "0").lower() in ("1", "true", "yes")


env_color = {
    "local": "lightgrey",
    "dev": "lightgreen",
    "development": "lightgreen",
    "staging": "yellow",
    "stg": "yellow",
    "prd": "red",
    "prod": "red",
    "production": "red",
}


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DB_NAME: str = Field(default=...)
    DB_PASSWORD: str = Field(default=...)
    DB_USERNAME: str = Field(default=...)
    DB_HOST: str = Field(default=...)
    DB_PORT: str = Field(default=...)
    DB_CONN_URL: str = Field(default=...)


class Settings(BaseSettings):
    # use `= Field(default=...)` as per https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    db_settings: DBSettings = Field(default_factory=DBSettings)
    api_env: str = os.getenv("API_ENV", DEFAULT_API_ENV)
    api_version: str = getattr(app, "__VERSION__", DEFAULT_API_VERSION)
    api_title: str = f"FastAPI demo ({api_env})"
    api_title_slug: str = api_title.lower().replace(" ", "-")
    api_description: str = (
        f'<span style="background-color: {env_color.get(api_env, DEFAULT_API_ENV)};font-size:15pt">(env: {api_env}) '
        "A simple [FastAPI](https://fastapi.tiangolo.com/)"
        "+ [asyncpg](https://techspot.zzzeek.org/2015/02/15/asynchronous-python-and-databases/) demo"
        "</span>"
    )
    api_contact: dict[str, str] = {
        "name": "Xiang ZHU",
        "url": "https://copdips.com/",
        "email": "xiang.zhu@outlook.com",
    }
    use_camel_case: bool = False

    debug: bool = api_env == DEFAULT_API_ENV
    testing: bool = (
        is_testing()
    )  # testing mode will use sqlite, and disable profiling middleware
    profiling: bool = not testing
    profiling_interval_seconds: float = 0.0001
    apitally_client_id: str = APITALLY_CLIENT_ID
    logging_level: int = logging.DEBUG if debug else logging.INFO


settings = Settings()
