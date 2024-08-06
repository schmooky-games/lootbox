import json
from typing import Union, List

from fastapi import APIRouter, Query

from src.exceptions import ErrorHTTPException
from src.lootboxes.schemas import LootboxTypes, LootboxDeactivate
from src.lootboxes.constants import LOOTBOX_NOT_FOUND, WRONG_LOOTBOX_TYPE, EMPTY_LOOTBOXES_LIST
from src.lootboxes.equal.schemas import EqualLootbox
from src.lootboxes.exclusive.schemas import ExclusiveLootbox
from src.lootboxes.utils.async_cache import AsyncCache
from src.lootboxes.weighted.schemas import WeightedLootbox
from src.redis_connection import redis

router = APIRouter()


lootbox_cache = AsyncCache(maxsize=1000)


@router.get("/lootboxes/{lootbox_id}", response_model=Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox],
            operation_id="get_lootbox",
            summary="Get lootbox by id")
async def get_lootbox(lootbox_id: str):
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(400, LOOTBOX_NOT_FOUND, f"Lootbox with id {lootbox_id} not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get('type')
    if lootbox_type == LootboxTypes.equal:
        lootbox = EqualLootbox(**lootbox_dict)
    elif lootbox_type == LootboxTypes.weighted:
        lootbox = WeightedLootbox(**lootbox_dict)
    elif lootbox_type == LootboxTypes.exclusive:
        lootbox = ExclusiveLootbox(**lootbox_dict)
    else:
        raise ErrorHTTPException(status_code=400, error_code=WRONG_LOOTBOX_TYPE, detail=f"Unknown lootbox type")

    return lootbox


@router.patch("/deactivate_lootbox/{lootbox_id}",
              response_model=Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox],
              operation_id="deactivate_lootbox",
              summary="Deactivate lootbox by id")
async def deactivate_lootbox(lootbox_id: str, update: LootboxDeactivate):
    lootbox_data = await redis.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_FOUND, detail="Lootbox not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get('type')
    if lootbox_type == LootboxTypes.equal:
        LootboxModel = EqualLootbox
    elif lootbox_type == LootboxTypes.weighted:
        LootboxModel = WeightedLootbox
    elif lootbox_type == LootboxTypes.exclusive:
        LootboxModel = ExclusiveLootbox
    else:
        raise ErrorHTTPException(status_code=400, error_code=666, detail=f"Unknown lootbox type")

    lootbox = LootboxModel.model_validate(lootbox_dict)

    update_data = update.dict(exclude_unset=True)
    updated_lootbox = lootbox.copy(update=update_data)

    await redis.set(lootbox_id, updated_lootbox.json())

    return updated_lootbox


@router.get("/lootboxes", response_model=List[Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox]],
            operation_id="get_lootboxes",
            summary="Get list of lootboxes")
async def get_lootboxes(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0)
):
    lootboxes = []
    cursor = 0

    while len(lootboxes) < limit:
        cursor, keys = await redis.scan(cursor, count=limit - len(lootboxes))

        for key in keys:
            if len(lootboxes) >= limit:
                break

            if offset > 0:
                offset -= 1
                continue

            lootbox_data = await lootbox_cache.get(key)
            if lootbox_data:
                lootbox_dict = json.loads(lootbox_data)
                lootbox_type = lootbox_dict.get('type')

                if lootbox_type == LootboxTypes.equal:
                    lootbox = EqualLootbox(**lootbox_dict)
                elif lootbox_type == LootboxTypes.weighted:
                    lootbox = WeightedLootbox(**lootbox_dict)
                elif lootbox_type == LootboxTypes.exclusive:
                    lootbox = ExclusiveLootbox(**lootbox_dict)
                else:
                    continue

                lootboxes.append(lootbox)

        if cursor == 0:
            break

    if len(lootboxes) == 0:
        return ErrorHTTPException(status_code=400, error_code=EMPTY_LOOTBOXES_LIST, detail="No lootboxes")

    return lootboxes


@router.get("/lootboxes_total_count")
async def total_count():
    lootboxes_count = await redis.dbsize()
    return {"total_count": lootboxes_count}
