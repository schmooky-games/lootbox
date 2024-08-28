import json
import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter

from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import (EMPTY_LOOTBOX, LOOTBOX_NOT_ACTIVE,
                                     LOOTBOX_NOT_FOUND, WRONG_LOOTBOX_TYPE)
from src.lootboxes.equal.schemas import (EqualItem, EqualLootbox,
                                         EqualLootboxUpd, Meta)
from src.lootboxes.schemas import LootboxTypes
from src.lootboxes.utils.async_cache import lootbox_cache
from src.lootboxes.utils.cuid_generator import CUID_GENERATOR
from src.redis_connection import redis

router = APIRouter()


@router.post("/create_lootbox", response_model=EqualLootbox, operation_id="create_equal_lootbox",
             summary="Create equal lootbox")
async def create_lootbox(items: List[Dict[str, Any]], name: str, draws_count: Optional[int] = None) -> EqualLootbox:
    lootbox_items = [
        EqualItem(
            id=CUID_GENERATOR.generate(),
            data=item.get("data", {}),
            meta=Meta(name=item.get("meta", {}).get("name", ""))
        )
        for item in items
    ]
    lootbox_id = CUID_GENERATOR.generate()
    lootbox_meta = Meta(name=name)
    lootbox = EqualLootbox(id=lootbox_id, meta=lootbox_meta, items=lootbox_items,
                           draws_count=draws_count, is_active=True)
    await redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


@router.patch("/update_lootbox/{lootbox_id}", response_model=EqualLootbox,
              operation_id="update_equal_lootbox",
              summary="Update equal lootbox content")
async def update_lootbox(lootbox_id: str, lootbox: EqualLootboxUpd) -> EqualLootbox:
    stored_lootbox_json = await redis.get(lootbox_id)
    stored_lootbox_dict = json.loads(stored_lootbox_json)

    lootbox_type = stored_lootbox_dict.get("type")
    if lootbox_type != LootboxTypes.equal:
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="This method allowed only for equal lootboxes"
        )

    stored_lootbox_model = EqualLootbox(**stored_lootbox_dict)

    updated_items = [EqualItem(data=item.data, meta=item.meta) for item in lootbox.items]
    update_data = lootbox.dict(exclude={"id", "type", "is_active"}, exclude_unset=True)
    update_data["items"] = updated_items
    updated_lootbox = stored_lootbox_model.copy(update=update_data)

    await lootbox_cache.update(lootbox_id, updated_lootbox.json())

    return updated_lootbox


@router.get("/get_loot/{lootbox_id}", response_model=EqualItem, operation_id="get_loot_from_equal_lootbox",
            summary="Get loot from equal lootbox")
async def get_loot(lootbox_id: str) -> EqualItem:
    lootbox_data = await lootbox_cache.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_FOUND, detail="Lootbox not found")

    lootbox_dict = json.loads(lootbox_data)

    lootbox_type = lootbox_dict.get("type")
    if lootbox_type != LootboxTypes.equal:
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="This method allowed only for equal lootboxes"
        )

    lootbox = EqualLootbox.model_validate_json(lootbox_data)

    if not lootbox.is_active:
        raise ErrorHTTPException(status_code=400, error_code=LOOTBOX_NOT_ACTIVE, detail="Lootbox is not active")

    if not lootbox.items:
        raise ErrorHTTPException(status_code=400, error_code=EMPTY_LOOTBOX, detail="No items in lootbox")

    drawed_item = secrets.choice(lootbox.items)

    return drawed_item
