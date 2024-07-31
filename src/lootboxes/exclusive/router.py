from fastapi import APIRouter
from typing import List, Dict, Any, Optional

from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import WRONG_LOOTBOX_TYPE
from src.lootboxes.schemas import Meta, WeightedItem, Lootbox
from src.lootboxes.utils import CUID_GENERATOR, AsyncCache
from src.lootboxes.weighted.utils import weighted_random
from src.redis_connection import redis

router = APIRouter()


@router.post("/create_lootbox", response_model=Lootbox, operation_id="create_exclusive_lootbox",
             summary="Crate exclusive lootbox")
async def create_lootbox(items: List[Dict[str, Any]], draws_count: Optional[int] = None):
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
    lootbox = Lootbox(id=lootbox_id, items=lootbox_items, draws_count=draws_count, is_active=True)
    await redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


lootbox_cache = AsyncCache()


@router.get("/get_loot/{lootbox_id}", response_model=WeightedItem, operation_id="get_loot_from_exclusive_box",
            summary="Get loot from weighted lootbox")
async def get_loot(lootbox_id: str):
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=1001, detail="Lootbox not found")

    lootbox = Lootbox.model_validate_json(lootbox_data)

    if not lootbox.is_active:
        raise ErrorHTTPException(status_code=400, error_code=1003, detail="Lootbox is not active")

    if not lootbox.items:
        raise ErrorHTTPException(status_code=400, error_code=1004, detail="No items in lootbox")

    if not lootbox.is_weighted():
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="Cannot get loot from equal lootbox using this endpoint"
        )

    weights = list([item.weight for item in lootbox.items])
    drawed_item = weighted_random(items=lootbox.items, weights=weights)

    lootbox.items.remove(drawed_item)
    updated_lootbox_data = lootbox.model_dump_json()
    await lootbox_cache.update(lootbox_id, updated_lootbox_data)

    return drawed_item
