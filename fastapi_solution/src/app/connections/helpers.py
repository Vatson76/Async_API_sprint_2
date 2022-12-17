import logging
from functools import wraps
from time import sleep
from typing import Union

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def backoff(start_sleep_time: Union[int, float] = 0.1, factor: int = 2, border_sleep_time: int = 10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                connection = await func(*args, **kwargs)
            except Exception as e:
                logger.exception('During connection to service, next error occurred')
                t = start_sleep_time
                logger.info(f'Reconnect in %d sec', t)
                while True:
                    sleep(t)
                    try:
                        connection = await func()
                        break
                    except Exception as e:
                        logger.exception('During connection to service, next error occurred')
                        t = t * 2 ** factor
                        t = t if t < border_sleep_time else border_sleep_time
                        logger.info(f'Cannot establish connection, reconnect in %d sec', t)
            return connection
        return inner
    return func_wrapper
