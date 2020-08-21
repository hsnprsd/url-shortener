import redis

import settings

redis_client = redis.Redis(
    host=settings.REDIS['host'],
    port=settings.REDIS['port'],
)
