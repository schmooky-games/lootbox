from redis.asyncio import Redis
from src.config import REDIS_URI


redis = Redis.from_url(REDIS_URI, encoding="utf-8", decode_responses=True)
