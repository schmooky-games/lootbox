from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from redis import Redis
import random
from cuid2 import Cuid

from src.config import REDIS_URI
from src.lootboxes.equal.models import Lootbox, Meta, Item

router = APIRouter()

redis = Redis.from_url(url=REDIS_URI)

CUID_GENERATOR = Cuid(length=10)


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


@router.post("/deactivate_lootbox/{lootbox_id}", response_model=Lootbox)
def deactivate_lootbox(lootbox_id: str):
    lootbox_data = redis.get(lootbox_id)
    if not lootbox_data:
        raise HTTPException(status_code=404, detail="Lootbox not found")
    lootbox = Lootbox.model_validate_json(lootbox_data)
    lootbox.is_active = False
    redis.set(lootbox_id, lootbox.model_dump_json())
    return lootbox


@router.get("/lootboxes", response_model=Dict[str, Lootbox])
def list_lootboxes():
    all_keys = redis.keys()
    lootboxes_data = {}

    for key in all_keys:
        lootbox_data = redis.get(key)
        if lootbox_data:
            lootbox = Lootbox.model_validate_json(lootbox_data)
            lootboxes_data[key.decode("utf-8")] = lootbox

    return lootboxes_data
