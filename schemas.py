from typing import Union
from pydantic import BaseModel

#create sport model
class SportBase(BaseModel):
    name: str
    imageUrl: str

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

#create notification model
class NotificationBase(BaseModel):
    name: str
    type: str
    redirectTo: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    seen: bool
    creationDate: str
    owner_id: int

    class Config:
        orm_mode = True

#match model
class MatchBase(BaseModel):
    date: str
    time: str
    status: str
    court: str
    city: str

class MatchCreate(MatchBase):
    sport_id: int
    level_id: int

#user model
class UserLogin(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    email: str
    name: str
    phoneNumber: str
    role: str
    university: str
    bornDate: str
    gender: str

class UserCreate(UserBase):
    password: str

class ImageCreate(BaseModel):
    imageUrl: str

#to manage concurrency
class User(UserBase):
    id: int
    imageUrl: str = None
    latitude: str = None
    longitude: str = None
    notifications: list[Notification] = []

    class Config:
        orm_mode = True

class Match(MatchBase):
    id: int
    creationDate: str = None
    rate: str = None
    user_created_id: int = None
    sport: Sport = None
    level: Level = None
    user_joined: User = None
    user_created: User = None

    class Config:
        orm_mode = True