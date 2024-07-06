from redis import Redis
from src.config import REDIS_URI

redis = Redis.from_url(REDIS_URI)
