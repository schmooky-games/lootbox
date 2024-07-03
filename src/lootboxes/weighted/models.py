from pydantic import BaseModel
from typing import List, Optional

from src.lootboxes.models import WeightedItem


class Lootbox(BaseModel):
    id: str
    items: List[WeightedItem]
    draws_count: Optional[int] = None
    is_active: bool = True
