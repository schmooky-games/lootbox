from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from src.lootboxes.schemas import Meta, LootboxTypes
from src.lootboxes.utils.cuid_generator import CUID_GENERATOR


class ExclusiveItem(BaseModel):
    id: str = Field(default_factory=CUID_GENERATOR.generate)
    data: Dict[str, Any]
    meta: Meta
    weight: float


class ExclusiveLootbox(BaseModel):
    id: str
    meta: Meta
    type: LootboxTypes = LootboxTypes.exclusive
    items: List[ExclusiveItem]
    draws_count: Optional[int] = None
    is_active: bool = True


class ExclusiveItemUpd(BaseModel):
    data: Dict[str, Any]
    meta: Meta
    weight: float


class ExclusiveLootboxUpd(BaseModel):
    meta: Meta
    items: List[ExclusiveItem]
    draws_count: Optional[int] = None
