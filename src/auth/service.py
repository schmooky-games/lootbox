from datetime import timedelta
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer

from src.auth.utils import redis

TOKEN_EXPIRATION = timedelta(hours=1)


def verify_token(token: HTTPBearer = Depends(HTTPBearer(auto_error=False))):

    if not token:
        raise HTTPException(status_code=401, detail="Not authorized")

    token_exists = redis.exists(f"token:{token.credentials}")
    if not token_exists:
        raise HTTPException(status_code=401, detail="Invalid token")

    redis.expire(f"token:{token.credentials}", int(TOKEN_EXPIRATION.total_seconds()))

    return token.credentials
