from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.models.mixins import UUIDMixin


class UserAuthHistory(UUIDMixin):
    """Модель истории авторизации пользователя."""

    user_id: UUID
    user_agent: str
    timestamp: datetime = Field(default=datetime.now())
