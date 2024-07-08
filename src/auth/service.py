import jwt
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from src.redis_connection import redis
from src.config import SECRET_KEY

TOKEN_EXPIRATION = timedelta(hours=1)


def verify_token(token: HTTPBearer = Depends(HTTPBearer(auto_error=False))):

    if not token:
        raise HTTPException(status_code=401, detail="Not authorized")

    token_exists = redis.exists(f"token:{token.credentials}")
    if not token_exists:
        raise HTTPException(status_code=401, detail="Invalid token")

    redis.expire(f"token:{token.credentials}", int(TOKEN_EXPIRATION.total_seconds()))

    return token.credentials


def generate_jwt_token():
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    payload = {
        'exp': expiration_time
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    redis_key = f"token:{token}"
    redis.setex(redis_key, 3600, "active")

    return token
