from redis.asyncio import Redis
from src.config import REDIS_URI


def create_redis_connection():
    return Redis.from_url(REDIS_URI, encoding="utf-8", decode_responses=True)


redis = create_redis_connection()
