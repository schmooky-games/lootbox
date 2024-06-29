from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class Meta(BaseModel):
    name: str


class Item(BaseModel):
    id: str
    data: Dict[str, Any]
    meta: Meta


class Lootbox(BaseModel):
    id: str
    items: List[Item]
    draws_count: Optional[int] = None
    is_active: bool = True

