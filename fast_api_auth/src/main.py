from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.routers import main_router
from src.core.config import project_settings, redis_settings
from src.db.init_postgres import create_first_superuser
from src.db.redis_cache import RedisCacheManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Контекст жизненного цикла FastAPI приложения.

    Управляет инициализацией и освобождением ресурсов при запуске и
    остановке приложения:
    - Создает первого суперпользователя при старте
    - Инициализирует подключение к Redis
    - Корректно закрывает соединения при завершении

    Yields:
        None: Приложение работает в этом контексте

    Note:
        Все операции в блоке try выполняются до запуска приложения,
        блок finally выполняется при остановке приложения.

    """
    redis_cache_manager = RedisCacheManager(redis_settings)
    try:
        await create_first_superuser()
        await redis_cache_manager.setup()

        yield

    finally:
        await redis_cache_manager.tear_down()


app = FastAPI(
    title=project_settings.project_auth_name,
    docs_url='/auth/openapi',
    openapi_url='/auth/openapi.json',
    default_response_class=ORJSONResponse,
    summary=project_settings.project_auth_summary,
    openapi_tags=project_settings.project_auth_tags,
    lifespan=lifespan,
)

app.include_router(main_router)
