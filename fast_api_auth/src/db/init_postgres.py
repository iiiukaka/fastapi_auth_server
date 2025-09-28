import contextlib

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from src.core.config import auth_settings
from src.core.user_core import get_user_db, get_user_manager
from src.db.postgres import get_async_session
from src.schemas.user_schema import UserCreate


get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
        email: EmailStr,
        password: str,
        is_superuser: bool = False
    ) -> None:
    """Создание нового пользователя в системе.

    Args:
        email: Email пользователя
        password: Пароль пользователя
        is_superuser: Флаг суперпользователя (по умолчанию False)

    Note:
        Если пользователь с таким email уже существует, исключение
        обрабатывается и функция завершается без ошибки.

    """
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser
                        )
                    )
    except UserAlreadyExists:
        pass


async def create_first_superuser() -> None:
    """Создание первого суперпользователя при инициализации приложения.

    Использует настройки из конфигурации для определения email и пароля.
    Создает пользователя только если указаны оба обязательных параметра.
    """
    if (auth_settings.first_superuser_email is not None
        and auth_settings.first_superuser_password is not None):
        await create_user(
            email=auth_settings.first_superuser_email,
            password=auth_settings.first_superuser_password,
            is_superuser=True,
        )
