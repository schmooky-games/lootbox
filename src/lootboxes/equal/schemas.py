from pydantic import BaseModel
from typing import List, Optional

from src.lootboxes.schemas import Item


class Lootbox(BaseModel):
    id: str
    items: List[Item]
    draws_count: Optional[int] = None
    is_active: bool = True
