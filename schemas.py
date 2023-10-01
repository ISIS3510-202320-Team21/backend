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

#match model
class MatchBase(BaseModel):
    date: str
    time: str
    status: str
    place: str
    sport_id: int
    level_id: int

class MatchCreate(MatchBase):
    pass

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

#to manage concurrency
class User(UserBase):
    id: int
    items: list[Item] = []
    image: Image = None
    notifications: list[Notification] = []
    matches: list[MatchBase] = []

    class Config:
        orm_mode = True

class Match(MatchBase):
    id: int
    rate: str
    users: list[UserBase] = []

    class Config:
        orm_mode = True