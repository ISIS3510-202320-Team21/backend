from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String, index=True)
    phoneNumber = Column(String, index=True)
    role = Column(String, index=True)
    bornDate = Column(String, index=True)
    gender = Column(String, index=True)

    items = relationship("Item", back_populates="owner")
    #images = relationship("Image", back_populates="owner")
    image = relationship("Image", uselist=False, backref="users")
    notifications = relationship("Notification", back_populates="owner")
    #matchesCreated = relationship("Match", back_populates="user1")
    #matchesJoined = relationship("Match", back_populates="user2")
    matches = relationship("Match", secondary="matches_users", back_populates="users")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    #owner = relationship("User", back_populates="images")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    redirectTo = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notifications")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    time = Column(String, index=True)
    rate = Column(String, index=True, nullable=True)
    status = Column(String, index=True)
    place = Column(String, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    #user1_id = Column(Integer, ForeignKey("users.id"))
    #user2_id = Column(Integer, ForeignKey("users.id"))

    sport = relationship("Sport", back_populates="matches") #, back_populates="matches"
    level = relationship("Level", back_populates="matches") #, back_populates="matches"
    users = relationship("User", secondary="matches_users", back_populates="matches")
    #user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches")
    #billing_address = relationship("Address", foreign_keys="[Customer.billing_address_id]")
    #user1 = relationship("User", foreign_keys=[user1_id])
    #user2 = relationship("User", foreign_keys=[user2_id])

#create MatchUser
class MatchUser(Base):
    __tablename__ = "matches_users"

    match_id = Column(Integer, ForeignKey("matches.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    matches = relationship("Match", back_populates="sport")

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    matches = relationship("Match", back_populates="level")