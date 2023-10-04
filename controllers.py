from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import or_
import datetime

#login functions
def login_user(db: Session, email: str, password: str):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user is None:
        return None
    if decode_password(db_user.hashed_password) == password:
        return db_user
    return "Wrong password"

def encode_password(password: str):
    return password + "notreallyhashed"

def decode_password(password: str):
    return password[:-15]

#user functions
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = encode_password(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        phoneNumber=user.phoneNumber,
        role=user.role,
        bornDate=user.bornDate,
        gender=user.gender,
        hashed_password=fake_hashed_password,
        university=user.university)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#image functions
def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).offset(skip).limit(limit).all()

def get_user_image(db: Session, user_id: int):
    return db.query(models.Image).filter(models.Image.owner_id == user_id).first()

def create_user_image(db: Session, image: schemas.ImageCreate, user_id: int):
    db_image = models.Image(**image.dict(), owner_id=user_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

#notification functions
def get_notifications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).offset(skip).limit(limit).all()

def get_user_notifications(db: Session, user_id: int):
    return db.query(models.Notification).filter(models.Notification.owner_id == user_id).all()

def create_user_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
    creationDate = datetime.datetime.now()
    seen = False
    db_notification = models.Notification(**notification.dict(), owner_id=user_id, creationDate=creationDate, seen=seen)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def update_notification(db: Session, notification_id: int):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    db_notification.seen = True
    db.commit()
    db.refresh(db_notification)
    return db_notification

#match functions
def get_matches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Match).offset(skip).limit(limit).all()

def create_user_match(db: Session, match: schemas.MatchCreate, user_id: int):
    creationDate = datetime.datetime.now()
    db_match = models.Match(**match.dict(), user_created_id=user_id, creationDate=creationDate)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_user_matches(db: Session, user_id: int):
    return db.query(models.Match).filter(or_(models.Match.user_created_id == user_id, models.Match.user_joined_id == user_id)).all()

def add_user_to_match(db: Session, match_id: int, user_id: int):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    db_match.user_joined_id = user_id
    db_match.status = "Joined"
    db.commit()
    db.refresh(db_match)
    return db_match

def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def add_rate_to_match(db: Session, match_id: int, rate: str):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    db_match.rate = rate
    db.commit()
    db.refresh(db_match)
    return db_match

def change_match_status(db: Session, match_id: int, status: str):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    db_match.status = status
    db.commit()
    db.refresh(db_match)
    return db_match

#sport functions
def get_sports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Sport).offset(skip).limit(limit).all()

def create_sport(db: Session, sport: schemas.SportCreate):
    db_sport = models.Sport(**sport.dict())
    db.add(db_sport)
    db.commit()
    db.refresh(db_sport)
    return db_sport

#level functions
def get_levels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Level).offset(skip).limit(limit).all()

def create_level(db: Session, level: schemas.LevelCreate):
    db_level = models.Level(**level.dict())
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level