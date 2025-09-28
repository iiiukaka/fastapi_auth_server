from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path

from src.core.user_core import current_superuser, current_user
from src.models.user import User
from src.schemas.response_schema import ResponseSchema
from src.schemas.role_schema import RoleCreate, RoleGetFull, RoleUpdate
from src.services.role_service import RoleService, get_role_service


router = APIRouter()


@router.get(
        '/all',
        response_model=list[RoleGetFull],
        summary='Get all roles',
        description='Get all roles'
    )
async def get_all_roles(
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_user)
) -> list[RoleGetFull]:
    """Получение списка всех ролей в системе.

    Args:
        role_service: Сервис для работы с ролями
        user: Текущий аутентифицированный пользователь
    Returns:
        list[RoleGetFull]: Список всех ролей с полной информацией

    """
    return await role_service.get_all()


@router.post(
        '/', response_model=RoleGetFull,
        summary='Create new role',
        description='Create new role'
    )
async def create_role(
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_superuser),
) -> RoleGetFull:
    """Создание новой роли в системе.

    Args:
        role_data: Данные для создания роли
        role_service: Сервис для работы с ролями
        user: Текущий суперпользователь

    Returns:
        RoleGetFull: Созданная роль с полной информацией

    Note:
        Требует прав суперпользователя

    """
    return await role_service.create(role_data)


@router.patch(
    '/{role_id}',
    response_model=RoleGetFull,
    summary='Update existing role',
    description='Update existing role'
)
async def update_role(
    role_id: Annotated[
        UUID,
        Path(
            title='role id',
            description='Role id for the item to search in the database',
        ),
    ],
    data: RoleUpdate,
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_superuser),
) -> RoleGetFull:
    """Обновление существующей роли.

    Args:
        role_id: UUID идентификатор роли
        data: Данные для обновления роли
        role_service: Сервис для работы с ролями
        user: Текущий суперпользователь

    Returns:
        RoleGetFull: Обновленная роль с полной информацией

    Note:
        Требует прав суперпользователя

    """
    return await role_service.update(role_id, data)


@router.delete(
    '/{role_id}',
    response_model=ResponseSchema,
    summary='Delete existing role',
    description='Delete existing role'
)
async def delete_role(
    role_id: Annotated[
        UUID,
        Path(
            title='role id',
            description='Role id for the item to search in the database',
        ),
    ],
    role_service: RoleService = Depends(get_role_service),
    user: User = Depends(current_superuser),
) -> ResponseSchema:
    """Удаление роли из системы.

    Args:
        role_id: UUID идентификатор роли для удаления
        role_service: Сервис для работы с ролями
        user: Текущий суперпользователь

    Returns:
        ResponseSchema: Сообщение об успешном удалении

    Note:
        Требует прав суперпользователя

    """
    await role_service.delete(role_id)
    return ResponseSchema(detail='Role deleted successfully')
