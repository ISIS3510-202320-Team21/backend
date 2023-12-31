from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
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
    university = Column(String, index=True)
    bornDate = Column(String, index=True)
    gender = Column(String, index=True)
    imageUrl = Column(String, nullable=True)
    latitude = Column(String, index=True, nullable=True)
    longitude = Column(String, index=True, nullable=True)

    notifications = relationship("Notification", back_populates="owner")

    matchesCreated = relationship("Match", foreign_keys="[Match.user_created_id]", back_populates="user_created")
    claimsCreated = relationship("Claim", foreign_keys="[Claim.user_created_id]", back_populates="user_created")
    matchesJoined = relationship("Match", foreign_keys="[Match.user_joined_id]", back_populates="user_joined")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)
    redirectTo = Column(String, index=True)
    seen = Column(Boolean, index=True)
    creationDate = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notifications")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    time = Column(String, index=True)
    rate1 = Column(String, index=True)
    rate2 = Column(String, index=True)
    status = Column(String, index=True)
    court = Column(String, index=True)
    city = Column(String, index=True)
    creationDate = Column(String, index=True)
    sport_id = Column(Integer, ForeignKey("sports.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    user_created_id = Column(Integer, ForeignKey("users.id"))
    user_joined_id = Column(Integer, ForeignKey("users.id"),nullable=True)

    sport = relationship("Sport", back_populates="matches")
    level = relationship("Level", back_populates="matches")
    
    user_created = relationship("User", foreign_keys=[user_created_id], back_populates="matchesCreated")
    user_joined = relationship("User", foreign_keys=[user_joined_id], back_populates="matchesJoined")


class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    imageUrl = Column(String, index=True)
    matches = relationship("Match", back_populates="sport")

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    matches = relationship("Match", back_populates="level")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    user_created_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)

    user_created = relationship("User", foreign_keys=[user_created_id], back_populates="claimsCreated")