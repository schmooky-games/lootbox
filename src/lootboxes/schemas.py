from enum import Enum

from pydantic import BaseModel


class LootboxTypes(str, Enum):
    equal = "equal"
    weighted = "weighted"
    exclusive = "exclusive"


class Meta(BaseModel):
    name: str


class LootboxUpdState(BaseModel):
    is_active: bool = False
