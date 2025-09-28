"""Импорты класса Base и всех моделей для Alembic."""
from src.db.postgres import Base
from src.models.auth_history import AuthHistory
from src.models.role import Role, UserRole
from src.models.user import User


__all__ = [
    Base,
    AuthHistory,
    Role,
    UserRole,
    User
]
