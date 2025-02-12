from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)

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
    db_settings: DBSettings = Field(default=DBSettings())
    api_name: str = "FastAPI demo"
    use_camel_case: bool = False
    repo_name: str = "fastapi-demo"
    # debug: bool = api_env == DEFAULT_API_ENV
    debug: bool = False


settings = Settings()
