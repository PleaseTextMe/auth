import os
from pydantic import SecretStr
from src.core.config import Settings, PostgresSettings, RedisSettings, ServiceSettings

def test_postgres_settings_connection_url():
    pg_settings = PostgresSettings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_DB="test_db",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password"
    )
    assert pg_settings.connection_url == "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"

def test_postgres_settings_connection_url_2():
    pg_settings = PostgresSettings(
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
        POSTGRES_DB="test_db",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password"
    )
    assert pg_settings.connection_url_2 == "postgresql+psycopg2://test_user:test_password@localhost:5432/test_db"

def test_redis_settings_url():
    redis_settings = RedisSettings(
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=1
    )
    assert redis_settings.url == "redis://localhost:6379/1"

def test_settings_initialization():
    settings = Settings()
    assert isinstance(settings.service, ServiceSettings)
    assert isinstance(settings.postgres, PostgresSettings)
    assert isinstance(settings.redis, RedisSettings)
