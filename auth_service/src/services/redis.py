import redis

from settings import settings

redis = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True
)
