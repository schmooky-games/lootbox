from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.lootboxes.schemas import LootboxTypes, Meta
from src.lootboxes.utils.cuid_generator import CUID_GENERATOR


class WeightedItem(BaseModel):
    id: str = Field(default_factory=CUID_GENERATOR.generate)
    data: Dict[str, Any]
    meta: Meta
    weight: float


class WeightedLootbox(BaseModel):
    id: str
    meta: Meta
    type: LootboxTypes = LootboxTypes.weighted
    items: List[WeightedItem]
    draws_count: Optional[int] = None
    is_active: bool = True


class WeightedItemUpd(BaseModel):
    data: Dict[str, Any]
    meta: Meta
    weight: float


class WeightedLootboxUpd(BaseModel):
    meta: Meta
    items: List[WeightedItemUpd]
    draws_count: Optional[int] = None
