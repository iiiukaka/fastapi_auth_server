from src.dependencies.auth_dependencies import (
    admin_required,
    any_authenticated,
    get_current_user,
    get_refresh_user,
    moderator_required,
    role_required,
    superuser_required,
)


# Экспортируем для обратной совместимости
__all__ = [
    'get_current_user',
    'get_refresh_user',
    'role_required',
    'admin_required',
    'superuser_required',
    'moderator_required',
    'any_authenticated'
]
