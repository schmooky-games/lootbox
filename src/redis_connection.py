from redis.asyncio import ConnectionPool, Redis
from src.config import REDIS_URI

redis_pool = ConnectionPool.from_url(
    REDIS_URI,
    encoding="utf-8",
    decode_responses=True,
    max_connections=500
)

redis = Redis(connection_pool=redis_pool)
