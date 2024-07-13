import secrets
from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from src.exceptions import ErrorHTTPException
from src.lootboxes.constants import WRONG_LOOTBOX_TYPE
from src.lootboxes.schemas import Meta, Item, Lootbox
from src.lootboxes.utils import CUID_GENERATOR
from src.redis_connection import redis

router = APIRouter()


@router.post("/create_lootbox", response_model=Lootbox)
async def create_lootbox(items: List[Dict[str, Any]], draws_count: Optional[int] = None):
    lootbox_items = [
        Item(
            id=CUID_GENERATOR.generate(),
            data=item.get('data', {}),
            meta=Meta(name=item.get('meta', {}).get('name', ''))
        )
        for item in items
    ]
    lootbox_id = CUID_GENERATOR.generate()
    lootbox = Lootbox(id=lootbox_id, items=lootbox_items, draws_count=draws_count, is_active=True)
    await redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


@router.get("/get_loot/{lootbox_id}", response_model=Item)
async def get_loot(lootbox_id: str):
    lootbox_data = await redis.get(lootbox_id)

    if not lootbox_data:
        raise ErrorHTTPException(status_code=400, error_code=1001, detail="Lootbox not found")

    lootbox = Lootbox.model_validate_json(lootbox_data)

    if not lootbox.is_active:
        raise ErrorHTTPException(status_code=400, error_code=1003, detail="Lootbox is not active")

    if not lootbox.items:
        raise ErrorHTTPException(status_code=400, error_code=1004, detail="No items in lootbox")

    if lootbox.is_weighted():
        raise ErrorHTTPException(
            status_code=400,
            error_code=WRONG_LOOTBOX_TYPE,
            detail="Cannot get loot from weighted lootbox using this endpoint"
        )

    drawed_item = secrets.choice(lootbox.items)

    return drawed_item
