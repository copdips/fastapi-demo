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
    """
    when using docker-compose, env vars will be injected by:

    ```docker-compose.yml
    env_file:
      - .env
    ```

    Even when using a dotenv file, pydantic will still read environment variables
    as well as the dotenv file, environment variables will always take priority over
    values loaded from a dotenv file.
    """

    # ! pydantic_settings tries to load settings from environment variables with the same name as the settings fields, then from a .env file, if SettingsConfigDict is set like below, and finally from the default value.
    # So we can load_env(override=True) at the beginning of the file, and then use the settings fields directly.
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


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    # for Azure Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = Field(default=...)
    # for Pydantic logfire
    LOGFIRE_TOKEN: str = Field(default=...)
    LOGFIRE_PROJECT_NAME: str = "fastapi-demo"
    # for sentry
    SENTRY_DSN: str = Field(default=...)


class Settings(BaseSettings):
    # use `= Field(default=...)` as per https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    db_settings: DBSettings = Field(default=DBSettings())
    # another way to set default value is to use default_factory
    logging_settings: LoggingSettings = Field(default_factory=lambda: LoggingSettings())
    api_env: str = os.getenv("API_ENV", DEFAULT_API_ENV)
    api_version: str = getattr(app, "__VERSION__", DEFAULT_API_VERSION)
    api_name: str = "FastAPI demo"
    api_title: str = f"{api_name} - ({api_env})"
    api_title_slug: str = f"{api_name} {api_env}".lower().replace(" ", "-")
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
    repo_name: str = "fastapi-demo"

    # debug: bool = api_env == DEFAULT_API_ENV
    testing: bool = (
        is_testing()
    )  # testing mode will use sqlite, and disable profiling middleware
    debug: bool = testing
    profiling: bool = not testing
    profiling_interval_seconds: float = 0.0001
    apitally_client_id: str = APITALLY_CLIENT_ID
    logging_level: int = logging.DEBUG if debug else logging.INFO
    logging_static_extra: dict[str, str] = {
        "api_version": api_version,
        "api_env": api_env,
        "api_title": api_title,
        "api_title_slug": api_title_slug,
    }
    enable_azure_monitor: bool = False
    # docker-compose use redis, but local docker use 127.0.0.1
    # when using local test without docker-compose: docker run --name my-redis -d redis:alpine
    redis_host: str = "127.0.0.1" if testing else f"{repo_name}-redis"
    rabbitmq_host: str = "127.0.0.1" if testing else f"{repo_name}-rabbitmq"
    rabbitmq_url: str = f"amqp://guest:guest@{rabbitmq_host}:5672/{api_title_slug}"
    celery_broker: str = rabbitmq_url
    celery_backend: str = f"redis://{redis_host}:6379/0"


settings = Settings()
