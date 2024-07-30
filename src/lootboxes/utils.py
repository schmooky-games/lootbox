from collections import OrderedDict
from cuid2 import Cuid

from src.redis_connection import redis

# CUID generator
CUID_GENERATOR = Cuid(length=10)


# async cache
class SimpleCache:
    def __init__(self, maxsize=1000):
        self.cache = OrderedDict()
        self.maxsize = maxsize

    async def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        value = await redis.get(key)
        if value is not None:
            if len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)
            self.cache[key] = value
        return value
