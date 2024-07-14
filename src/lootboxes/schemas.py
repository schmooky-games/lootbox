from pydantic import BaseModel, field_validator, Field
from typing import List, Dict, Any, Optional, Union


class Meta(BaseModel):
    name: str


class Item(BaseModel):
    id: str
    data: Dict[str, Any]
    meta: Meta


class WeightedItem(Item):
    weight: float


class Lootbox(BaseModel):
    id: str
    items: List[Union[Item, WeightedItem]] = Field(..., alias="items")
    draws_count: Optional[int] = None
    is_active: bool = True

    @field_validator('items', mode='before')
    def validate_items(cls, v):
        return [WeightedItem(**item) if isinstance(item, dict) and 'weight' in item
            else Item(**item) if isinstance(item, dict)
            else item
            for item in v]

    def is_weighted(self) -> bool:
        return any(isinstance(item, WeightedItem) for item in self.items)

    class Config:
        populate_by_name = True
