from snowflake import SnowflakeGenerator

from src.core.config import settings

_generator = SnowflakeGenerator(settings.service.worker_id)


def generate_snowflake_id() -> int:
    return next(_generator)
