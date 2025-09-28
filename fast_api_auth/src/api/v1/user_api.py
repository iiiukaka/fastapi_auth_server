from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.core.config import project_settings
from src.core.user_core import (
    UserManager,
    auth_backend,
    current_user,
    fastapi_users,
    get_user_manager,
    refresh_auth_backend,
)
from src.db.redis_cache import RedisClientFactory
from src.models.user import User
from src.schemas.user_schema import UserCreate, UserRead, UserUpdate


router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/jwt',
    tags=['auth'],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=['auth'],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes if route.name != 'users:delete_user'
]
router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)


@router.post(
    '/refresh',
    tags=['auth'],
    summary='Refresh Access Token',
    description=(
        'Refreshes the access token. Returns a new access token if successful.'
    ),
)
async def refresh_access_token(
    request: Request,
    user_manager: UserManager = Depends(get_user_manager),
    user: User = Depends(current_user)
) -> dict[str, str]:
    """Обновление access token с использованием refresh token из cookies.

    Проверяет валидность refresh token из cookies против хранилища Redis
    и выдает новый access token при успешной проверке.

    Возвращает:
        dict: Новый access token в формате {'access_token': 'значение_токена'}

    Исключения:
        HTTPException: 401 если refresh token недействителен или отсутствует
    """
    refresh_token = request.cookies.get('refresh_token')
    redis = await RedisClientFactory.create(project_settings.redis_dsn)
    payload = await refresh_auth_backend.get_strategy().read_token(
        refresh_token, user_manager
    )

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный токен обновления',
        )

    stored_refresh_token = await redis.get(f'refresh_token:{payload.id}')

    if stored_refresh_token.decode('utf-8') != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный токен обновления',
        )

    new_access_token = await auth_backend.get_strategy().write_token(payload)

    return {'access_token': new_access_token}
