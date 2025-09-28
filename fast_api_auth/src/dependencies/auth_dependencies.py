from fastapi import Depends, HTTPException, Request, status

from src.services.token_service import TokenService


class AuthException(HTTPException):
    """Унифицированное исключение для ошибок аутентификации."""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        target: str = 'authentication'
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={
                'message': message,
                'code': error_code,
                'target': target
            }
        )


async def extract_token_data(
        request: Request, token_type: str = 'access'
    ) -> dict[str, any]:
    """Извлечение и валидация данных из токена."""
    token_name = f'{token_type}_token'
    token = request.cookies.get(token_name)

    if not token:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=f'{token_type.capitalize()} token is missing',
            error_code=f'MISSING_{token_type.upper()}_TOKEN'
        )

    try:
        payload = TokenService.decode_jwt(token)

        # Проверяем, что токен содержит необходимые поля
        if token_type == 'access' and 'role' not in payload:
            raise AuthException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message='Access token missing role information',
                error_code='INVALID_ACCESS_TOKEN_FORMAT'
            )

        return payload

    except HTTPException:
        raise
    except Exception:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=f'Invalid {token_type} token',
            error_code=f'INVALID_{token_type.upper()}_TOKEN'
        )


async def get_current_user(request: Request) -> dict[str, any]:
    """Основная зависимость для получения текущего пользователя."""
    return await extract_token_data(request, 'access')


async def get_refresh_user(request: Request) -> dict[str, any]:
    """Зависимость для получения пользователя из refresh токена."""
    return await extract_token_data(request, 'refresh')


async def validate_refresh_token(request: Request) -> dict[str, any]:
    """Зависимость для валидации refresh токена (проверка в Redis)."""
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Refresh token is missing',
            error_code='MISSING_REFRESH_TOKEN'
        )

    # Декодируем токен для получения user_id
    payload = TokenService.decode_jwt(refresh_token)
    user_id = payload.get('sub')

    if not user_id:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Refresh token missing user identifier',
            error_code='INVALID_REFRESH_TOKEN_FORMAT'
        )

    # Проверяем токен в Redis
    is_valid = await TokenService.validate_refresh_token(
        refresh_token, user_id
    )
    if not is_valid:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message='Invalid or expired refresh token',
            error_code='INVALID_REFRESH_TOKEN'
        )

    return payload


class PermissionChecker:
    """Универсальный проверщик прав доступа."""

    @staticmethod
    def has_required_role(
        user_roles: list[str], required_roles: list[str]
    ) -> bool:
        """Проверяет, есть ли у пользователя необходимая роль."""
        if not user_roles or not required_roles:
            return False

        # Если roles - строка, преобразуем в список
        if isinstance(user_roles, str):
            user_roles = [user_roles]
        elif not isinstance(user_roles, list):
            return False

        user_roles_set = set(user_roles)
        required_roles_set = set(required_roles)

        return bool(user_roles_set & required_roles_set)

    @staticmethod
    def has_all_roles(
        user_roles: list[str], required_roles: list[str]
    ) -> bool:
        """Проверяет, есть ли у пользователя все требуемые роли."""
        if not user_roles or not required_roles:
            return False

        if isinstance(user_roles, str):
            user_roles = [user_roles]
        elif not isinstance(user_roles, list):
            return False

        user_roles_set = set(user_roles)
        required_roles_set = set(required_roles)

        return required_roles_set.issubset(user_roles_set)


def role_required(required_roles: list[str]):
    """Фабрика зависимостей для проверки ролей."""

    async def _role_checker(
            user_data: dict[str, any] = Depends(get_current_user)
        ) -> dict[str, any]:
        user_role = user_data.get('role', [])

        if not PermissionChecker.has_required_role(user_role, required_roles):
            raise AuthException(
                status_code=status.HTTP_403_FORBIDDEN,
                message='Insufficient permissions',
                error_code='INSUFFICIENT_PERMISSIONS',
                target='role'
            )

        return user_data

    return _role_checker


# Предопределенные зависимости для часто используемых ролей
admin_required = role_required(['admin'])
superuser_required = role_required(['superuser', 'admin'])
moderator_required = role_required(['moderator', 'admin'])
any_authenticated = role_required(['user', 'moderator', 'admin', 'superuser'])
