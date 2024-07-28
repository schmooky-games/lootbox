
from fastapi import APIRouter

from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import LOOTBOX_NOT_FOUND, EMPTY_LOOTBOXES_LIST
from src.lootboxes.schemas import Lootbox
from src.redis_connection import redis

router = APIRouter()


@router.get("/lootbox/{lootbox_id}", response_model=Lootbox, operation_id="get_lootbox",
            summary="Get lootbox by id")
async def get_lootbox(lootbox_id: str):
    lootbox_data = await redis.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(400, LOOTBOX_NOT_FOUND, f"Lootbox with id {lootbox_id} not found")

    lootbox = Lootbox.model_validate_json(lootbox_data)
    return lootbox


@router.post("/deactivate_lootbox/{lootbox_id}", response_model=Lootbox, operation_id="deactivate_lootbox",
             summary="Deactivate lootbox by id")
async def deactivate_lootbox(lootbox_id: str):
    lootbox_data = await redis.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(400, LOOTBOX_NOT_FOUND, f"Lootbox with id {lootbox_id} not found")

    lootbox = Lootbox.model_validate_json(lootbox_data)
    lootbox.is_active = False
    await redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


# @router.get("/lootboxes", response_model=Dict[str, Lootbox])
# def list_lootboxes():
#     all_keys = redis.keys()
#     lootboxes_data = {}
#
#     if len(all_keys) == 0:
#         raise ErrorHTTPException(400, EMPTY_LOOTBOXES_LIST, "Lootboxes list is empty")
#
#     for key in all_keys:
#         if not key.decode("utf-8").startswith("token:"):
#             lootbox_data = redis.get(key)
#             if lootbox_data:
#                 lootbox = Lootbox.model_validate_json(lootbox_data)
#                 lootboxes_data[key.decode("utf-8")] = lootbox
#
#     return lootboxes_data
