from typing import Dict

from cuid2 import Cuid
from fastapi import APIRouter, HTTPException
from redis import Redis

from src.config import REDIS_URI
from src.lootboxes.schemas import Lootbox

router = APIRouter()
redis = Redis.from_url(url=REDIS_URI)
CUID_GENERATOR = Cuid(length=10)


@router.get("/lootbox/{lootbox_id}", response_model=Lootbox)
def get_lootbox(lootbox_id: str):
    lootbox_data = redis.get(lootbox_id)
    lootbox = Lootbox.model_validate_json(lootbox_data)
    return lootbox


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
