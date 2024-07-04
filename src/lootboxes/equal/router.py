from fastapi import HTTPException, APIRouter
from typing import List, Dict, Any, Optional

import random

from src.lootboxes.schemas import Meta, Item
from src.lootboxes.equal.schemas import Lootbox
from src.lootboxes.router import CUID_GENERATOR, redis

router = APIRouter()

@router.post("/create_lootbox", response_model=Lootbox)
def create_lootbox(items: List[Dict[str, Any]], draws_count: Optional[int] = None):
    lootbox_items = [
        Item(id=CUID_GENERATOR.generate(), data=item.get('data', {}), meta=Meta(name=item.get('meta', {}).get('name', '')))
        for item in items
    ]
    lootbox_id = CUID_GENERATOR.generate()
    lootbox = Lootbox(id=lootbox_id, items=lootbox_items, draws_count=draws_count, is_active=True)
    redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


@router.get("/get_loot/{lootbox_id}", response_model=Item)
def get_loot(lootbox_id: str):
    lootbox_data = redis.get(lootbox_id)
    if not lootbox_data:
        raise HTTPException(status_code=404, detail="Lootbox not found")
    lootbox = Lootbox.model_validate_json(lootbox_data)

    if not lootbox.is_active:
        raise HTTPException(status_code=404, detail="Lootbox is not active")

    if not lootbox.items:
        raise HTTPException(status_code=404, detail="No items in lootbox")

    drawed_item = random.choice(lootbox.items)

    return drawed_item
