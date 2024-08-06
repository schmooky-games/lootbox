from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from src.lootboxes.schemas import Meta, LootboxTypes
from src.lootboxes.utils.cuid_generator import CUID_GENERATOR


class EqualItem(BaseModel):
    id: str = Field(default_factory=CUID_GENERATOR.generate)
    data: Dict[str, Any]
    meta: Meta


class EqualLootbox(BaseModel):
    id: str
    meta: Meta
    type: LootboxTypes = LootboxTypes.equal
    items: List[EqualItem]
    draws_count: Optional[int] = None
    is_active: bool = True


class EqualItemUpd(BaseModel):
    data: Dict[str, Any]
    meta: Meta


class EqualLootboxUpd(BaseModel):
    meta: Meta
    items: List[EqualItemUpd]
    draws_count: Optional[int] = None

