from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from redis import Redis
import random
from cuid2 import Cuid

app = FastAPI()
redis = Redis(host='redis', port=6379, db=0)


class Item(BaseModel):
    item_id: str
    weight: Optional[int] = None


class Lootbox(BaseModel):
    type: str
    items: List[Item]
    draws_count: Optional[int] = None


CUID_GENERATOR: Cuid = Cuid(length=10)


@app.post("/lootbox/create")
def create_lootbox(lootbox: Lootbox):
    if lootbox.type == "equal":
        for item in lootbox.items:
            item.weight = None
    elif lootbox.type == "weighted":
        if not all(item.weight for item in lootbox.items):
            raise HTTPException(status_code=400, detail="All items must have weights for weighted lootbox")

    lootbox_id = CUID_GENERATOR.generate()
    redis.set(lootbox_id, lootbox.json())
    return {"lootbox_id": lootbox_id}


@app.get("/lootbox/{lootbox_id}/draw")
def draw_item(lootbox_id: str):
    lootbox_data = redis.get(lootbox_id)
    if not lootbox_data:
        raise HTTPException(status_code=404, detail="Lootbox not found")

    lootbox = Lootbox.model_validate_json(lootbox_data)
    if lootbox.type == "equal":
        item = random.choice(lootbox.items)
        return {"item_id": item.item_id}

    elif lootbox.type == "weighted":
        total_weight = sum(item.weight for item in lootbox.items)
        rnd = random.uniform(0, total_weight)
        upto = 0
        for item in lootbox.items:
            if upto + item.weight >= rnd:
                return {"item_id": item.item_id}
            upto += item.weight

    elif lootbox.type == "unique":
        item = random.choice(lootbox.items)
        lootbox.items.remove(item)
        redis.set(lootbox_id, lootbox.json())
        return {"item_id": item.item_id}

    raise HTTPException(status_code=500, detail="Error in drawing item")


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
