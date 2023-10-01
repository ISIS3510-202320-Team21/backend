from typing import Union
from pydantic import BaseModel

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

#create sport model
class SportBase(BaseModel):
    name: str

class SportCreate(SportBase):
    pass

class Sport(SportBase):
    id: int

    class Config:
        orm_mode = True

#create level model
class LevelBase(BaseModel):
    name: str

class LevelCreate(LevelBase):
    pass

class Level(LevelBase):
    id: int

    class Config:
        orm_mode = True

#create image model
class ImageBase(BaseModel):
    image: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

#create notification model
class NotificationBase(BaseModel):
    name: str
    type: str
    redirectTo: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

#create match model
class MatchBase(BaseModel):
    date: str
    time: str
    rate: str
    status: str
    place: str

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int
    sport_id: int
    level_id: int
    user1_id: int
    user2_id: int

    class Config:
        orm_mode = True

#user model
class UserBase(BaseModel):
    email: str
    name: str
    phoneNumber: str
    role: str
    bornDate: str
    gender: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    items: list[Item] = []
    image: list[Image] = []
    notifications: list[Notification] = []
    matches: list[Match] = []

    class Config:
        orm_mode = True