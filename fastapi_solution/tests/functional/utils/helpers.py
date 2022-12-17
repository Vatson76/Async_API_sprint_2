from functools import wraps
from time import sleep
from typing import Generator, List


def backoff(
    start_sleep_time: float = 0.1,
    factor: int = 2,
    border_sleep_time: int = 10
):
    """
    A function to re-execute the function after a while if an error occurs.
    Uses a naive exponential growth of the repeat time (factor) to the
    boundary time waiting (border_sleep_time).

    :param start_sleep_time: initial repeat time
    :param factor: how many times should the waiting time be increased
    :param border_sleep_time: boundary waiting time
    :return: result of the function
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            n = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    n += 1
                    if sleep_time >= border_sleep_time:
                        sleep_time = border_sleep_time
                    else:
                        sleep_time = min(
                            sleep_time * (factor ** n),
                            border_sleep_time
                        )
                    sleep(sleep_time)
        return inner
    return func_wrapper


def gendata(data: List[dict], index: str) -> Generator:
    """Generates structure of the index documents."""
    for row in data:
        yield {
            '_index': index,
            '_id': row['id'],
            '_source': row
        }


def delete_docs(docs: List[dict], index: str) -> Generator:
    """Deletes list of documents in index."""
    for doc in docs:
        yield {
            '_op_type': 'delete',
            '_index': index,
            '_id': doc['id'],
        }
