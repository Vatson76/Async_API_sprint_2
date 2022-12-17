import os
import sys

from helpers import backoff
from redis import Redis

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings  # noqa


@backoff()
def wait_for_redis():
    redis_db = Redis(**test_settings.REDIS_DSN.dict())
    if not redis_db.ping():
        raise Exception


if __name__ == '__main__':
    wait_for_redis()
