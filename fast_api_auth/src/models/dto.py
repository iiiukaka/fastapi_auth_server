from pydantic import BaseModel, ConfigDict


class AbstractDTO(BaseModel):
    """Абстрактная DTO (Data Transfer Object) модель с базовой конфигурацией.

    Настройки модели:
    - from_attributes: Разрешает создание модели из атрибутов объектов
    - populate_by_name: Разрешает использование псевдонимов полей при валидации
    - use_enum_values: Автоматически преобразует enum в их значения
    - arbitrary_types_allowed: Разрешает использование
    произвольных типов данных
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )
