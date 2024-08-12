import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter

from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import (EMPTY_LOOTBOX, LOOTBOX_NOT_ACTIVE,
                                     LOOTBOX_NOT_FOUND, WRONG_LOOTBOX_TYPE)
from src.lootboxes.exclusive.schemas import (ExclusiveItem, ExclusiveLootbox,
                                             ExclusiveLootboxUpd, Meta)
from src.lootboxes.schemas import LootboxTypes
from src.lootboxes.utils.async_cache import lootbox_cache
from src.lootboxes.utils.cuid_generator import CUID_GENERATOR
from src.lootboxes.utils.weighted_random import weighted_random
from src.redis_connection import redis

router = APIRouter()


@router.post("/create_lootbox", response_model=ExclusiveLootbox, operation_id="create_exclusive_lootbox",
             summary="Create exclusive lootbox")
async def create_lootbox(items: List[Dict[str, Any]], name: str, draws_count: Optional[int] = None):
    lootbox_items = [
        ExclusiveItem(
            id=CUID_GENERATOR.generate(),
            data=item.get("data", {}),
            meta=Meta(name=item.get("meta", {}).get("name", "")),
            weight=item.get("weight", 1.0)
        )
        for item in items
    ]
    lootbox_id = CUID_GENERATOR.generate()
    lootbox_meta = Meta(name=name)
    lootbox = ExclusiveLootbox(id=lootbox_id, meta=lootbox_meta, items=lootbox_items,
                               draws_count=draws_count, is_active=True)
    await redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


@router.patch("/update_lootbox/{lootbox_id}", response_model=ExclusiveLootbox,
              operation_id="update_exclusive_lootbox",
              summary="Update exclusive lootbox content")
async def update_lootbox(lootbox_id: str, lootbox: ExclusiveLootboxUpd):
    stored_lootbox_json = await redis.get(lootbox_id)
    stored_lootbox_data = json.loads(stored_lootbox_json)

    lootbox_type = stored_lootbox_data.get("type")
    if lootbox_type != LootboxTypes.exclusive:
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="This method allowed only for exclusive lootboxes"
        )

    stored_lootbox_model = ExclusiveLootbox(**stored_lootbox_data)
    updated_items = [ExclusiveItem(data=item.data, meta=item.meta, weight=item.weight) for item in lootbox.items]
    update_data = lootbox.dict(exclude={"id", "type", "is_active"}, exclude_unset=True)
    update_data["items"] = updated_items
    updated_lootbox = stored_lootbox_model.copy(update=update_data)

    await lootbox_cache.update(lootbox_id, updated_lootbox.json())

    return updated_lootbox


@router.get("/get_loot/{lootbox_id}", response_model=ExclusiveItem, operation_id="get_loot_from_exclusive_box",
            summary="Get loot from weighted lootbox")
async def get_loot(lootbox_id: str):
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_FOUND, detail="Lootbox not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get("type")
    if lootbox_type != LootboxTypes.exclusive:
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="This method allowed only for exclusive lootboxes"
        )

    lootbox = ExclusiveLootbox.model_validate_json(lootbox_data)

    if not lootbox.is_active:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_ACTIVE, detail="Lootbox is not active")

    if not lootbox.items:
        raise ErrorHTTPException(status_code=400, error_code=EMPTY_LOOTBOX, detail="No items in lootbox")

    weights = [item.weight for item in lootbox.items]
    drawed_item = weighted_random(items=lootbox.items, weights=weights)

    lootbox.items.remove(drawed_item)
    updated_lootbox_data = lootbox.model_dump_json()
    await lootbox_cache.update(lootbox_id, updated_lootbox_data)

    return drawed_item
