import json
from typing import List, Union, Dict

from fastapi import APIRouter, Query

from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import (EMPTY_LOOTBOXES_LIST, LOOTBOX_NOT_FOUND,
                                     WRONG_LOOTBOX_TYPE, UKNOWN_LOOTBOX_TYPE)
from src.lootboxes.equal.schemas import EqualLootbox
from src.lootboxes.exclusive.schemas import ExclusiveLootbox
from src.lootboxes.schemas import LootboxUpdState, LootboxTypes
from src.lootboxes.utils.async_cache import lootbox_cache
from src.lootboxes.weighted.schemas import WeightedLootbox
from src.redis_connection import redis

router = APIRouter()


@router.get("/lootboxes/{lootbox_id}", response_model=Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox],
            operation_id="get_lootbox",
            summary="Get lootbox by id")
async def get_lootbox(lootbox_id: str) -> Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox]:
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(400, LOOTBOX_NOT_FOUND, f"Lootbox with id {lootbox_id} not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get("type")
    if lootbox_type == LootboxTypes.equal:
        lootbox = EqualLootbox(**lootbox_dict)
    elif lootbox_type == LootboxTypes.weighted:
        lootbox = WeightedLootbox(**lootbox_dict)
    elif lootbox_type == LootboxTypes.exclusive:
        lootbox = ExclusiveLootbox(**lootbox_dict)
    else:
        raise ErrorHTTPException(status_code=400, error_code=WRONG_LOOTBOX_TYPE, detail="Unknown lootbox type")

    return lootbox


@router.patch("/deactivate_lootbox/{lootbox_id}",
              response_model=Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox],
              operation_id="deactivate_lootbox",
              summary="Deactivate lootbox by id")
async def deactivate_lootbox(lootbox_id: str, update: LootboxUpdState)\
        -> Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox]:
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_FOUND, detail="Lootbox not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get("type")
    if lootbox_type == LootboxTypes.equal:
        LootboxModel = EqualLootbox
    elif lootbox_type == LootboxTypes.weighted:
        LootboxModel = WeightedLootbox
    elif lootbox_type == LootboxTypes.exclusive:
        LootboxModel = ExclusiveLootbox
    else:
        raise ErrorHTTPException(status_code=400, error_code=UKNOWN_LOOTBOX_TYPE, detail="Unknown lootbox type")

    lootbox = LootboxModel.model_validate(lootbox_dict)

    update_data = update.dict(exclude_unset=True)
    update_data["is_active"] = False
    updated_lootbox = lootbox.copy(update=update_data)

    await lootbox_cache.update(lootbox_id, updated_lootbox.json())

    return updated_lootbox


@router.patch("/activate_lootbox/{lootbox_id}",
              response_model=Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox],
              operation_id="activate_lootbox",
              summary="Activate lootbox by id")
async def activate_lootbox(lootbox_id: str, update: LootboxUpdState)\
        -> Union[EqualLootbox, WeightedLootbox]:
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_FOUND, detail="Lootbox not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get("type")
    if lootbox_type == LootboxTypes.equal:
        LootboxModel = EqualLootbox
    elif lootbox_type == LootboxTypes.weighted:
        LootboxModel = WeightedLootbox
    elif lootbox_type == LootboxTypes.exclusive:
        LootboxModel = ExclusiveLootbox
    else:
        raise ErrorHTTPException(status_code=400, error_code=UKNOWN_LOOTBOX_TYPE, detail="Unknown lootbox type")

    lootbox = LootboxModel.model_validate(lootbox_dict)

    update_data = update.dict(exclude_unset=True)
    update_data["is_active"] = True
    updated_lootbox = lootbox.copy(update=update_data)

    await lootbox_cache.update(lootbox_id, updated_lootbox.json())

    return updated_lootbox


@router.get("/lootboxes", response_model=List[Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox]])
async def get_lootboxes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str = Query(None, min_length=1)
) -> List[Union[EqualLootbox, WeightedLootbox, ExclusiveLootbox]]:
    lootboxes = []
    cursor = 0
    total_scanned = 0

    while len(lootboxes) < limit:
        cursor, keys = await redis.scan(cursor, count=100)

        for key in keys:
            if len(lootboxes) >= limit:
                break

            total_scanned += 1
            if total_scanned <= offset:
                continue

            lootbox_data = await redis.get(key)
            if not lootbox_data:
                continue

            lootbox_dict = json.loads(lootbox_data)

            lootbox_type = lootbox_dict.get("type")
            lootbox_name = lootbox_dict.get("meta")["name"].lower()

            if search and search.lower() not in lootbox_name:
                continue

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

    if not lootboxes:
        raise ErrorHTTPException(status_code=400, error_code=EMPTY_LOOTBOXES_LIST, detail="No lootboxes found")

    return lootboxes


@router.get("/lootboxes_total_count")
async def total_count() -> Dict[str, int]:
    lootboxes_count = await redis.dbsize()
    return {"total_count": lootboxes_count}
