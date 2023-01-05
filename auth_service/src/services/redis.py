import redis

from settings import settings

redis = redis.StrictRedis(
    host=settings.REDIS_AUTH_HOST, port=settings.REDIS_AUTH_PORT, db=0, decode_responses=True
)
