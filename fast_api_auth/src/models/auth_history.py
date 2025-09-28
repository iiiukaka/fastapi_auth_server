from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.postgres import Base


class AuthHistory(Base):
    """Таблица истории аутентификации пользователя."""

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    user_agent: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.now, nullable=False
    )

    user: Mapped['User'] = relationship('User', back_populates='auth_history')
