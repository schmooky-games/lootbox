from redis import Redis
from src.config import REDIS_URI

redis = Redis.from_url(url=REDIS_URI)