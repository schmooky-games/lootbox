from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union


class Meta(BaseModel):
    name: str


class Item(BaseModel):
    id: str
    data: Dict[str, Any]
    meta: Meta


class WeightedItem(Item):
    weight: float


class LootboxResponse(BaseModel):
    id: str
    items: List[Union[Item, WeightedItem]]
    draws_count: Optional[int] = None
    is_active: bool = True
