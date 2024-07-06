from cuid2 import Cuid
from redis import Redis

from src.config import REDIS_URI

redis = Redis.from_url(url=REDIS_URI)
CUID_GENERATOR = Cuid(length=10)
