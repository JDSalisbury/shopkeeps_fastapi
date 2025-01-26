from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: int
    quantity: int
    damage: Optional[str] = Field(default=None)
    armor_class: Optional[str] = Field(default=None)
    shopkeep_id: Optional[int] = Field(default=None, foreign_key="shopkeep.id")

    shopkeep: Optional["ShopKeep"] = Relationship(back_populates="inventory")


class ShopKeep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
    sex: str
    shop_name: str
    description: str
    character_class: str
    voice: str
    personality: str
    gold: int
    shop_type: str
    friendship_level: int
    image_url: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    inventory: List[Item] = Relationship(back_populates="shopkeep")
