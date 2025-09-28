import re
import uuid
from typing import AsyncIterator

from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    declared_attr,
    mapped_column,
    sessionmaker,
)

from src.core.config import postgres_settings, project_settings


class PreBase:
    """Базовый класс для всех моделей SQLAlchemy."""

    @declared_attr
    def __tablename__(self) -> str:
        """Добавляет название таблицы по названию класса.

        в метаданные модели в стиле snake_case.
        """
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self.__name__).lower()

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, sort_order=-1
    )


"""Базовый класс для всех декларативных моделей."""
Base = declarative_base(cls=PreBase)

"""Асинхронный движок для подключения к PostgreSQL."""
engine = create_async_engine(
    postgres_settings.dsn, echo=project_settings.debug
)

"""Фабрика асинхронных сессий для работы с базой данных."""
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Генератор асинхронных сессий для использования в зав-тях FastAPI."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
