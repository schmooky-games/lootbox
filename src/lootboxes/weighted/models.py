from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Meta(BaseModel):
    name: str


class Item(BaseModel):
    id: str
    data: Dict[str, Any]
    meta: Meta
    weight: float


class Lootbox(BaseModel):
    id: str
    items: List[Item]
    draws_count: Optional[int] = None
    is_active: bool = True
