from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy import or_
import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func
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
def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def delete_user(db: Session, user_db: schemas.User):
    db.delete(user_db)
    db.commit()

def update_user_image(db: Session, user_id: int, image: schemas.ImageCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.imageUrl = image.imageUrl
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_location(db: Session, user_id: int, latitude: str, longitude: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.latitude = latitude
    db_user.longitude = longitude
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserBase):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        db_user.email = user.email
        db_user.name = user.name
        db_user.phoneNumber = user.phoneNumber
        db_user.role = user.role
        db_user.university = user.university
        db_user.bornDate = user.bornDate
        db_user.gender = user.gender
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        return e.args[0]

def change_password(db: Session, user_id: int, old_password: str, new_password: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if decode_password(db_user.hashed_password) == old_password:
        db_user.hashed_password = encode_password(new_password)
        db.commit()
        db.refresh(db_user)
        return db_user
    return "Wrong password"

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
def delete_notification(db: Session, notification_id: int):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not db_notification:
        return None
    db.delete(db_notification)
    db.commit()
    return db_notification
#match functions
def get_matches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Match).offset(skip).limit(limit).all()

def get_matches_by_sport(db: Session, sport_id: int):
    return db.query(models.Match).filter(models.Match.sport_id == sport_id).all()

def create_user_match(db: Session, match: schemas.MatchCreate, user_id: int):
    creationDate = datetime.datetime.now()
    db_match = models.Match(**match.dict(), user_created_id=user_id, creationDate=creationDate)
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db.query(models.Match)\
        .options(joinedload(models.Match.sport))\
        .options(joinedload(models.Match.user_created))\
        .options(joinedload(models.Match.user_joined))\
        .options(joinedload(models.Match.level))\
        .filter(models.Match.id == db_match.id).first()

def get_match_by_id(db: Session, match_id: int):
    return db.query(models.Match)\
        .options(joinedload(models.Match.sport))\
        .options(joinedload(models.Match.user_created))\
        .options(joinedload(models.Match.user_joined))\
        .options(joinedload(models.Match.level))\
        .filter(models.Match.id == match_id).first()

def delete_match(db: Session, db_match: schemas.Match):
    db.delete(db_match)
    db.commit()


def get_user_matches(db: Session, user_id: int):
    return db.query(models.Match).filter(or_(models.Match.user_created_id == user_id, models.Match.user_joined_id == user_id)).all()



def add_user_to_match(db: Session, match_id: int, user_id: int):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    db_match.user_joined_id = user_id
    db_match.status = "Approved"
    db.commit()
    db.refresh(db_match)
    return db.query(models.Match)\
        .options(joinedload(models.Match.sport))\
        .options(joinedload(models.Match.user_created))\
        .options(joinedload(models.Match.user_joined))\
        .options(joinedload(models.Match.level))\
        .filter(models.Match.id == db_match.id).first()

def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def add_rate_to_match(db: Session, match_id: int, rate: str,is_user_created: bool):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if is_user_created:
        db_match.rate1 = rate
    else:
        db_match.rate2 = rate
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

def get_sport_by_id(db: Session, sport_id: int):
    return db.query(models.Sport).filter(models.Sport.id == sport_id).first()

def delete_sport(db: Session, sport_id: int):
    db_sport = get_sport_by_id(db, sport_id)
    if not db_sport:
        return None
    db.delete(db_sport)
    db.commit()
    return db_sport

#level functions
def get_levels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Level).offset(skip).limit(limit).all()

def get_level(db: Session, level_id: int):
    return db.query(models.Level).filter(models.Level.id == level_id).first()

def delete_level(db: Session, level_id: int):
    db_level = get_level(db, level_id)
    db.delete(db_level)
    db.commit()

def create_level(db: Session, level: schemas.LevelCreate):
    db_level = models.Level(**level.dict())
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level

#get universities, this is a list of strings fixed in the code
def get_universities():
    return ["Universidad de los Andes", "Universidad Nacional", "Pontificia Universidad Javeriana", "Universidad del Rosario", "Universidad Externado", "Universidad de la Sabana", "Universidad Sergio Arboleda", "Universidad de la Salle", "Universidad del Bosque", "Other"]

#get roles, this is a list of strings fixed in the code
def get_roles():
    return ["Student", "Professor", "Graduated", "Other"]

#get genders, this is a list of strings fixed in the code
def get_genders():
    return ["Male","Female","Other"]

#get cities, this is a list of strings fixed in the code
def get_cities():
    return ["Bogotá","Medellín","Cali","Barranquilla","Cartagena","Cúcuta","Soledad","Ibagué","Bucaramanga","Soacha","Santa Marta","Villavicencio","Bello","Valledupar","Pereira","Montería","Pasto","Manizales"]

def get_courts():
    return [
        "Parque Deportivo Andino",
        "Complejo Atlético Caribe",
        "Cancha de Fútbol Cafetero",
        "Arena Amazonia",
        "Cancha Valle del Cauca",
        "Complejo Deportivo Bolívar",
        "Domo de los Llanos",
        "Estadio Antioqueño",
        "Polideportivo Santander",
        "Coliseo de los Conquistadores"
    ]

# Claim services
def get_claim(db: Session, claim_id: int):
    return db.query(models.Claim).filter(models.Claim.id == claim_id).first()

def get_claims(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Claim).offset(skip).limit(limit).all()

# def create_claim(db: Session, claim: schemas.ClaimBase):
#     db_claim = models.Claim(
#         user_created_id = claim.user_created_id,
#         content = claim.content)
#     db.add(db_claim)
#     db.commit()
#     db.refresh(db_claim)
#     return db_claim

def create_claim(db: Session, claim: schemas.ClaimCreate):
    db_claim = models.Claim(**claim.dict())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim


def get_user_matches_count_by_sport(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    # Asegúrate de que las fechas están en formato de cadena de texto que coincida con tu base de datos.
    start_date_str = start_date.strftime('%d/%m/%Y')
    end_date_str = end_date.strftime('%d/%m/%Y')
    return (
        db.query(models.Sport.name, models.Sport.imageUrl, func.count(models.Match.id).label('match_count'))
        .join(models.Match, models.Sport.id == models.Match.sport_id)
        .filter(
            (models.Match.user_created_id == user_id) | 
            (models.Match.user_joined_id == user_id), 
            # Usa las cadenas de texto para la comparación
            models.Match.date.between(start_date_str, end_date_str),
            models.Match.status != "Deleted"
        )
        .group_by(models.Sport.name, models.Sport.imageUrl)
        .all()
    )

