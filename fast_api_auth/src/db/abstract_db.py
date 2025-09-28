from abc import ABC, abstractmethod


class AbstractDAO(ABC):
    """Абстрактный DAO для операций поиска в БД."""

    @abstractmethod
    async def get(self, table: str, id_obj: str) -> dict[str, str] | None:
        """Получение объекта по ID из указанной таблицы."""
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        table: str,
        offset: int = 0,
        limit: int = 50,
        sort: list[dict[str, str]] | None = None,
        filters: dict[str, any] | None = None,
    ) -> list[dict[str, any]]:
        """Поиск объектов в таблице."""
        raise NotImplementedError
