import os
import redis

redis_url = os.getenv("REDIS_URL")

if redis_url:
    redis_client = redis.from_url(redis_url)
else:
    redis_client = None