
from src.core.config import PostgresSettings, RedisSettings, ServiceSettings, settings


def test_service_settings_defaults():
    service = ServiceSettings()
    assert service.project_name == "auth"
    assert service.worker_id == 0


def test_postgres_settings_url():
    pg = PostgresSettings()
    assert pg.connection_url == "postgresql+asyncpg://test_user:test_password@127.0.0.1:5435/please_text_me_test_db"


def test_redis_settings_url():
    redis = RedisSettings()
    assert redis.url == "redis://127.0.0.1:6380/0"


def test_global_settings_singleton():
    assert settings.service is not None
    assert settings.postgres is not None
    assert settings.redis is not None
