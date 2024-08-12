import time
from datetime import datetime, timedelta
from typing import Dict

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from redis.asyncio import Redis

from src.config import SECRET_KEY
from src.redis_connection import redis

TOKEN_EXPIRATION = timedelta(hours=1)
CACHE_CAPACITY = 10000


class TokenCache:
    def __init__(self, capacity: int):
        self.cache: Dict[str, float] = {}
        self.capacity = capacity

    def insert(self, token: str, expiration: float):
        if len(self.cache) >= self.capacity:
            oldest_token = min(self.cache, key=self.cache.get)
            del self.cache[oldest_token]
        self.cache[token] = expiration

    def contains(self, token: str) -> bool:
        if token in self.cache:
            if self.cache[token] > time.time():
                return True
            del self.cache[token]
        return False


token_cache = TokenCache(CACHE_CAPACITY)


async def verify_token(
        token: HTTPBearer = Depends(HTTPBearer(auto_error=False)),
        redis: Redis = Depends(lambda: redis)
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authorized")

    if token_cache.contains(token.credentials):
        return token.credentials

    token_key = f"token:{token.credentials}"
    token_ttl = await redis.ttl(token_key)

    if token_ttl <= 0:
        raise HTTPException(status_code=401, detail="Invalid token")

    expiration = time.time() + token_ttl
    token_cache.insert(token.credentials, expiration)

    return token.credentials


async def generate_jwt_token():
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    payload = {
        'exp': expiration_time
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    redis_key = f"token:{token}"
    await redis.setex(redis_key, 3600, "active")

    return token
