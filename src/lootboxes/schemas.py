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
        if isinstance(v, list) and all(isinstance(item, (Item, WeightedItem)) for item in v):
            return v
        validated_items = []
        for item in v:
            if isinstance(item, dict):
                if 'weight' in item:
                    validated_items.append(WeightedItem(**item))
                else:
                    validated_items.append(Item(**item))
            elif isinstance(item, (Item, WeightedItem)):
                validated_items.append(item)
            else:
                raise ValueError(f"Invalid item type: {type(item)}")
        return validated_items

    def is_weighted(self) -> bool:
        return any(isinstance(item, WeightedItem) for item in self.items)

    class Config:
        populate_by_name = True
