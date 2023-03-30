from typing import Union
from enum import Enum
from pydantic import BaseModel


class Image(BaseModel):
    file: bytes


class sexStatus(str, Enum):
    male = "m"
    female = "f"


class Image_64(BaseModel):
    front_down: str
    front_up: str
    side_down: str
    side_up: str


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UpdateUser(BaseModel):
    email: Union[str, None] = None
    password: Union[str, None] = None


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True
