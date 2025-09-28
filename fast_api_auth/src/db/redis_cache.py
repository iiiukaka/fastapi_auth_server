from abc import ABC, abstractmethod

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError as RedisError

from src.core.config import RedisSettings
from src.utils.backoff import backoff


class CacheInterface(ABC):
    """Абстрактный интерфейс для управления кеш-подключениями."""

    @abstractmethod
    async def connect(self) -> None:
        """Инициализирует подключение к сервису кеширования."""

    @abstractmethod
    async def close(self) -> None:
        """Корректно закрывает подключение к сервису кеширования."""


class RedisCache(CacheInterface):
    """Реализация кеш-менеджера для работы с Redis.

    Attributes:
        redis_client: Асинхронный клиент Redis

    """

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self.redis_client = redis_client

    async def connect(self) -> None:
        """Настраивает интеграцию FastAPI с Redis бэкендом."""
        FastAPICache.init(
            RedisBackend(self.redis_client),
            prefix='fastapi-cache'
        )

    async def close(self) -> None:
        """Завершает работу с Redis, освобождает соединения."""
        await self.redis_client.close()


class RedisClientFactory:
    """Фабрика для создания клиента Redis."""

    @staticmethod
    async def create(redis_dsn: str) -> aioredis.Redis:
        """Создает новое подключение к Redis.

        Args:
            redis_dsn: DSN для подключения к Redis в формате redis://...

        Returns:
            Асинхронный клиент Redis

        """
        return await aioredis.from_url(redis_dsn)


class RedisCacheManager:
    """Менеджер жизненного цикла Redis подключения и кеширования.

    Attributes:
        settings: Конфигурационные настройки приложения
        redis_client: Подключение к Redis (инициализируется при вызове setup)
        cache: Реализация интерфейса кеширования

    """

    def __init__(self, settings: RedisSettings) -> None:
        self.settings = settings
        self.redis_client: aioredis.Redis | None = None
        self.cache: CacheInterface | None = None

    @backoff(RedisError)
    async def setup(self) -> None:
        """Инициализирует подключение к Redis с обработкой ошибок.

        Raises:
            RedisError: При невозможности установить соединение после повторов

        """
        self.redis_client = await RedisClientFactory.create(
            self.settings.dsn
        )
        self.cache = RedisCache(self.redis_client)
        await self.cache.connect()

    @backoff(RedisError)
    async def tear_down(self) -> None:
        """Корректно завершает работу с Redis.

        Закрывает все соединения и освобождает ресурсы.
        """
        if self.cache:
            await self.cache.close()
