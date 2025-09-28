import logging
import time
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from redis.exceptions import ConnectionError as RedisError


P = ParamSpec('P')
R = TypeVar('R')

logger = logging.getLogger(__name__)


def backoff(
    error_connection: type[RedisError],
    start_sleep_time: float = 0.1,
    factor: int = 2,
    border_sleep_time: float = 10.0,
    max_attempts: int = 15,
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    """Backoff для повторного выполнения при ошибках."""

    def func_wrapper(func: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R | None:
            sleep_time: float = start_sleep_time
            attempts: int = 0

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except error_connection as error:
                    attempts += 1
                    sleep_time = min(sleep_time * 2**factor, border_sleep_time)

                    logger.exception(
                        'Ошибка подключения в функции '
                        f'{func.__name__}: {error}. '
                        f'Повторная попытка через {sleep_time} секунд... '
                        f'(Попытка {attempts}/{max_attempts})'
                    )

                    time.sleep(sleep_time)

            logger.error(
                f'Достигнуто максимальное количество попыток '
                f'в функции {func.__name__}. '
                f'Функция завершилась с ошибкой.'
            )
            return None

        return inner

    return func_wrapper
