import os
from logging import config as logging_config
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ServiceSettings(ModelConfig):
    base_dir: Path = Path(__file__).parent.parent.parent
    project_name: str = Field(default="auth", validation_alias="PROJECT_NAME")
    worker_id: int = Field(default=0, validation_alias="WORKER_ID")
    debug: bool = Field(default=True, validation_alias="DEBUG")


class PostgresSettings(ModelConfig):
    host: str = Field(default="127.0.0.1", validation_alias="POSTGRES_HOST")
    port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    db_name: str = Field(default="please_text_me_db", validation_alias="POSTGRES_DB")
    user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    password: SecretStr = Field(..., validation_alias="POSTGRES_PASSWORD")
    echo: bool = Field(default=False, validation_alias="POSTGRES_ECHO")

    @property
    def connection_url(self) -> str:
        return URL.create("postgresql+asyncpg", username=self.user,
                          password=self.password.get_secret_value(), host=self.host,
                          port=self.port, database=self.db_name).render_as_string(hide_password=False)

    @property
    def connection_url_2(self) -> str:
        return URL.create("postgresql+psycopg2", username=self.user,
                          password=self.password.get_secret_value(), host=self.host,
                          port=self.port, database=self.db_name).render_as_string(hide_password=False)


class RedisSettings(ModelConfig):
    host: str = Field(default="127.0.0.1", validation_alias="REDIS_HOST")
    port: int = Field(default=6379, validation_alias="REDIS_PORT")
    db: int = Field(default=0, validation_alias="REDIS_DB")

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    service: ServiceSettings = ServiceSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
