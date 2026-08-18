import logging

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import clear_mappers

from src.core.config import settings
from src.infrastructure.db import postgres, redis
from src.infrastructure.models import start_mappers
from src.interfaces.lifetime import AbstractAppLifetime

logger = logging.getLogger(__name__)


class AppLifetime(AbstractAppLifetime):
    async def startup(self) -> None:
        await self._connect_to_postgres()
        await self._connect_to_redis()
        # await self._connect_to_rabbitmq()

    async def shutdown(self) -> None:
        await self._disconnect_from_postgres()
        await self._disconnect_from_redis()
        # await self._disconnect_from_rabbitmq()
        clear_mappers()

    # async def _connect_to_rabbitmq(self) -> None:
    #     producer.producer = producer.RabbitMQProducer(
    #         connection_url=settings.rabbit.connection_url,
    #         exchange_name=settings.rabbit.exchange_name,
    #     )
    #     await producer.producer.connect()

    # async def _disconnect_from_rabbitmq(self) -> None:
    #     if producer.producer is not None:
    #         await producer.producer.close()
    #     logger.info("Отключение от RabbitMQ")

    async def _connect_to_postgres(self) -> None:
        postgres.engine = create_async_engine(url=settings.postgres.connection_url, echo=settings.postgres.echo)
        postgres.session_maker = async_sessionmaker(postgres.engine, expire_on_commit=False, class_=AsyncSession)
        try:
            async with postgres.engine.begin() as _:
                logger.info("✅ Соединение с базой данных успешно установлено")
                start_mappers()
        except Exception as e:
            logger.error(
                "❌ Ошибка при установлении соединения с базой данных %s: %s", settings.postgres.connection_url, e
            )
            raise e

    async def _disconnect_from_postgres(self) -> None:
        if postgres.engine is not None:
            await postgres.engine.dispose()
        logger.info("Отключение от Postgres")

    async def _connect_to_redis(self) -> None:
        redis.redis_client = Redis.from_url(settings.redis.url)
        try:
            await redis.redis_client.ping()
            logger.info("✅ Соединение с Redis успешно установлено")
        except Exception as e:
            logger.error("❌ Ошибка при соединении с Redis %s: %s", settings.redis.url, e)
            raise e

    async def _disconnect_from_redis(self) -> None:
        if redis.redis_client is not None:
            await redis.redis_client.aclose()
            logger.info("Отключение от Redis")
