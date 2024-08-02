import json

from fastapi import APIRouter
from typing import List, Dict, Any, Optional, Union

from src.lootboxes.schemas import LootboxTypes
from src.lootboxes.utils.async_cache import AsyncCache
from src.lootboxes.utils.weighted_random import weighted_random
from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import WRONG_LOOTBOX_TYPE, LOOTBOX_NOT_ACTIVE, LOOTBOX_NOT_FOUND, EMPTY_LOOTBOX
from src.lootboxes.weighted.schemas import Meta, WeightedLootbox, WeightedItem, WeightedLootboxUpd
from src.lootboxes.utils.cuid_generator import CUID_GENERATOR
from src.redis_connection import redis


router = APIRouter()


@router.post("/create_lootbox", response_model=WeightedLootbox, operation_id="create_weighted_lootbox",
             summary="Create weighted lootbox")
async def create_lootbox(items: List[Dict[str, Union[Any, float]]], draws_count: Optional[int] = None):
    lootbox_items = [
        WeightedItem(
            id=CUID_GENERATOR.generate(),
            data=item.get('data', {}),
            meta=Meta(name=item.get('meta', {}).get('name', '')),
            weight=item.get('weight', 1.0)
        )
        for item in items
    ]
    lootbox_id = CUID_GENERATOR.generate()
    lootbox = WeightedLootbox(id=lootbox_id, items=lootbox_items, draws_count=draws_count, is_active=True)
    await redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


@router.patch("/update_lootbox/{lootbox_id}", response_model=WeightedLootbox,
              operation_id="update_weighted_lootbox",
              summary="Update weighted lootbox content")
async def update_lootbox(lootbox_id: str, lootbox: WeightedLootboxUpd):
    stored_lootbox_json = await redis.get(lootbox_id)
    stored_lootbox_data = json.loads(stored_lootbox_json)

    lootbox_type = stored_lootbox_data.get('type')
    if lootbox_type != LootboxTypes.weighted:
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="This method allowed only for weighted lootboxes"
        )

    stored_lootbox_model = WeightedLootbox(**stored_lootbox_data)
    updated_items = [WeightedItem(data=item.data, meta=item.meta, weight=item.weight) for item in lootbox.items]
    update_data = lootbox.dict(exclude={'id', 'type', 'is_active'}, exclude_unset=True)
    update_data['items'] = updated_items
    updated_lootbox = stored_lootbox_model.copy(update=update_data)

    await redis.set(lootbox_id, updated_lootbox.json())

    return updated_lootbox


lootbox_cache = AsyncCache(maxsize=1000)


@router.get("/get_loot/{lootbox_id}", response_model=WeightedItem, operation_id="get_loot_from_weighted_lootbox",
            summary="Get loot from weighted lootbox")
async def get_loot(lootbox_id: str):
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_FOUND, detail="Lootbox not found")

    lootbox_dict = json.loads(lootbox_data)

    if not lootbox_dict.get('is_active', False):
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_ACTIVE, detail="Lootbox is not active")

    lootbox_type = lootbox_dict.get('type')
    if lootbox_type != LootboxTypes.weighted:
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="This method allowed only for weighted lootboxes"
        )

    lootbox = WeightedLootbox.model_validate_json(lootbox_data)

    if not lootbox.items:
        raise ErrorHTTPException(status_code=400, error_code=EMPTY_LOOTBOX, detail="No items in lootbox")

    weights = list([item.weight for item in lootbox.items])
    drawed_item = weighted_random(items=lootbox.items, weights=weights)

    return drawed_item
