from uuid import UUID

from pydantic import field_validator

from src.models.dto import AbstractDTO
from src.models.role import Permissions


class RoleCreate(AbstractDTO):
    """Схема для создания роли."""

    name: str
    permissions: list[Permissions]

    @field_validator('permissions')
    @classmethod
    def _check_permissions(
        cls,
        value: list[Permissions] | None
    ) -> list[Permissions]:
        """Проверяет, что список разрешений не пустой."""
        if value is None:
            return None
        if len(value) == 0:
            raise ValueError("Permissions can't be empty")
        return value


class RoleUpdate(AbstractDTO):
    """Схема для обновления роли."""

    name: str | None = None
    permissions: list[Permissions] | None = None


class RoleGetFull(RoleCreate):
    """Схема для получения полной информации о роли."""

    id: UUID
