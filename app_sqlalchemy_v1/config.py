from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# load_dotenv(override=True)


def get_default_user(prefix: str, suffix: str) -> str:
    # This function can do any custom logic.
    return f"{prefix}_{suffix}"


class AppSettings(BaseSettings):
    # Configure Pydantic to load environment variables from .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    env: str

    # If an environment variable (by default "USER" in uppercase) exists,
    # its value will be used. Otherwise, the lambda calling get_default_user is invoked.
    user: str = Field(
        default_factory=lambda data: get_default_user(data["env"], "hihi")
    )


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

    DB_NAME: str = Field(default=...)
    DB_PASSWORD: str = Field(default=...)
    DB_USERNAME: str = Field(default=...)
    DB_HOST: str = Field(default=...)
    DB_PORT: str = Field(default=...)
    DB_CONN_URL: str = Field(default=...)


class Settings(BaseSettings):
    # use `= Field(default=...)` as per https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
    # db_settings: DBSettings = Field(default=DBSettings())
    env: str = "development"
    app_settings: AppSettings = Field(default=AppSettings(env=env))
    api_name: str = "FastAPI demo"
    use_camel_case: bool = False
    repo_name: str = "fastapi-demo"
    # debug: bool = api_env == DEFAULT_API_ENV
    debug: bool = False


settings = Settings()
breakpoint()
