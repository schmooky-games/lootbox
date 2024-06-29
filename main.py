from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Any
# from redis import Redis
import random
from cuid2 import Cuid

from models.models import Lootbox, Meta, Item

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(docs_url="/api")
# redis = Redis(host='redis', port=6379, db=0)
Instrumentator().instrument(app).expose(app)
CUID_GENERATOR: Cuid = Cuid(length=10)


lootboxes = {}


@app.post("/create_lootbox", response_model=Lootbox)
def create_lootbox(items: List[Dict[str, Any]], draws_count: Optional[int] = None):
    lootbox_items = [
        Item(id=CUID_GENERATOR.generate(), data=item.get('data', {}), meta=Meta(name=item.get('meta', {}).get('name', '')))
        for item in items
    ]
    lootbox_id = CUID_GENERATOR.generate()
    lootbox = Lootbox(id=lootbox_id, items=lootbox_items, draws_count=draws_count, is_active=True)
    lootboxes[lootbox_id] = lootbox
    # redis.set(lootbox_id, lootbox.json())
    return lootbox


@app.get("/get_loot/{lootbox_id}", response_model=Item)
def get_loot(lootbox_id: str):
    # lootbox_data = redis.get(lootbox_id)
    # if not lootbox_data:
    #     raise HTTPException(status_code=404, detail="Lootbox not found")
    #
    # lootbox = Lootbox.model_validate_json(lootbox_data)
    if lootbox_id not in lootboxes:
        raise HTTPException(status_code=404, detail="Lootbox not found")

    lootbox = lootboxes[lootbox_id]

    if not lootbox.is_active:
        raise HTTPException(status_code=404, detail="Lootbox is not active")

    if not lootbox.items:
        raise HTTPException(status_code=404, detail="No items in lootbox")

    drawed_item = random.choice(lootbox.items)

    return drawed_item


@app.post("/deactivate_lootbox/{lootbox_id}", response_model=Lootbox)
def deactivate_lootbox(lootbox_id: str):
    if lootbox_id not in lootboxes:
        raise HTTPException(status_code=404, detail="Lootbox not found")

    lootbox = lootboxes[lootbox_id]
    lootbox.is_active = False
    return lootbox


@app.get("/lootboxes", response_model=Dict[str, Lootbox])
def list_lootboxes():
    return lootboxes


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
