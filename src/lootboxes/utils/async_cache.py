import copy
from collections import OrderedDict

from src.redis_connection import redis


class AsyncCache:
    def __init__(self, maxsize=10000):
        self.cache = OrderedDict()
        self.maxsize = maxsize

    async def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return copy.deepcopy(self.cache[key])
        value = await redis.get(key)
        if value is not None:
            if len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)
            self.cache[key] = value
        return copy.deepcopy(value)

    async def update(self, key, value):
        if key in self.cache:
            del self.cache[key]
        await redis.set(key, value)


lootbox_cache = AsyncCache()
