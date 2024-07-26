from fastapi import APIRouter, Depends

from src.auth.service import verify_token, generate_jwt_token

router = APIRouter()


# @router.post("/login")
# def login(token: str):
#     token_exists = redis_client.exists(f"token:{token}")
#     if not token_exists:
#         raise HTTPException(status_code=401, detail="Неверный токен")
#     redis_client.expire(f"token:{token}", int(TOKEN_EXPIRATION.total_seconds()))
#     return {"token": token, "message": "Вход выполнен успешно"}


@router.post("/generate")
async def generate_token():
    token = await generate_jwt_token()
    return {"Token set in redis"}


protected_router = APIRouter(dependencies=[Depends(verify_token)])


@protected_router.get("/me")
def check_token(current_user: str = Depends(verify_token)):
    return {"Your token": f"{current_user}"}


# @protected_router.post("/logout")
# def logout(token: HTTPBearer = Depends(HTTPBearer())):
#     redis_client.delete(f"token:{token.credentials}")
#     return {"message": "Выход выполнен успешно"}


router.include_router(protected_router)
