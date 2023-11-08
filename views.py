import asyncio
from fastapi import Depends, FastAPI, HTTPException, Query, WebSocketDisconnect
from psycopg2 import IntegrityError
from psycopg2.errors import UniqueViolation
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import controllers, models, schemas
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from models import User, Match, Sport
from sqlalchemy import func, desc, and_
from datetime import datetime, timezone
import schedule
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import time
import threading
from fastapi import WebSocket

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Deshabilita las redirecciones automáticas para barras al final

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origines (no usar en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos o puedes especificar: ["GET", "POST"]
    allow_headers=["*"],  # Permite todos los headers o puedes especificar los que necesitas
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#login functions
@app.post("/login/", response_model=schemas.User) #
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = controllers.login_user(db, email=user.email, password=user.password)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif db_user == "Wrong password":
        raise HTTPException(status_code=404, detail="Wrong password")
    return db_user

#user functions
@app.post("/users/", response_model=schemas.User) #
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = controllers.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return controllers.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User]) #
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = controllers.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User) #
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = controllers.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}/", response_model=schemas.User) #
def update_user(user: schemas.UserBase, user_id: int, db: Session = Depends(get_db)):
    db_user = controllers.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif isinstance(db_user, str):
        error_message = db_user
        raise HTTPException(status_code=400, detail="Email already registered")
    return db_user

@app.put("/users/{user_id}/password/", response_model=schemas.User) #
def change_password(old_password: str, new_password: str, user_id: int, db: Session = Depends(get_db)):
    db_user = controllers.change_password(db, user_id=user_id, old_password=old_password, new_password=new_password)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif db_user == "Wrong password":
        raise HTTPException(status_code=404, detail="Wrong password")
    return db_user

@app.post("/users/{user_id}/image/", response_model=schemas.User) #
def update_user_image(image: schemas.ImageCreate, user_id: int, db: Session = Depends(get_db)):
    db_user = controllers.update_user_image(db, user_id=user_id, image=image)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}/location/", response_model=schemas.User) #
def update_user_location(latitude: str, longitude: str, user_id: int, db: Session = Depends(get_db)):
    db_user = controllers.update_user_location(db, user_id=user_id, latitude=latitude, longitude=longitude)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/user/{user_id}/most_reserved_sports_this_week/")
def get_most_reserved_sports_this_week(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now()
    monday_of_this_week = today - timedelta(days=today.weekday())
    monday_of_this_week = (today - timedelta(days=today.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    start_of_week = monday_of_this_week.strftime('%Y-%m-%d %H:%M:%S.%f')

    sports_counts = (
        db.query(
            Match.sport_id.label("id"),
            Sport.name,
            Sport.imageUrl.label("imageUrl"),  
            func.count(Match.sport_id).label("count")
        )
        .join(Sport, Match.sport_id == Sport.id)
        .filter(
            and_(
                (Match.user_created_id == user_id) | (Match.user_joined_id == user_id),
                Match.creationDate >= start_of_week
            )
        )
        .group_by(Match.sport_id, Sport.name, Sport.imageUrl)  # Incluye Sport.imageUrl en el group_by
        .order_by(desc("count"))
        .limit(2)
        .all()
    )

    if not sports_counts:
        random_sports = (
            db.query(Sport.id, Sport.name, Sport.imageUrl)  # Añade Sport.imageUrl
            .order_by(func.random())
            .limit(2)
            .all()
        )

        if not random_sports:
            raise HTTPException(status_code=404, detail="No sports available")

        random_sports_counts = [{"id": sport.id, "name": sport.name, "imageUrl": sport.imageUrl, "count": 0} for sport in random_sports]
        return random_sports_counts

    # Convierte la respuesta a un formato que incluya la URL de la imagen
    result = [{"id": sport.id, "name": sport.name, "imageUrl": sport.imageUrl, "count": sport.count} for sport in sports_counts]
    return result

@app.delete("/users/{user_id}/", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = controllers.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    controllers.delete_user(db, db_user)
    return db_user

#notification functions
@app.post("/users/{user_id}/notifications/", response_model=schemas.Notification)
def create_notification_for_user(
    user_id: int, notification: schemas.NotificationCreate, db: Session = Depends(get_db)
):
    return controllers.create_user_notification(db=db, notification=notification, user_id=user_id)

@app.get("/notifications/", response_model=list[schemas.Notification])
def read_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notifications = controllers.get_notifications(db, skip=skip, limit=limit)
    return notifications

@app.get("/users/{user_id}/notifications/", response_model=list[schemas.Notification])
def read_user_notifications(user_id: int, db: Session = Depends(get_db)):
    db_notifications = controllers.get_user_notifications(db, user_id=user_id)
    if db_notifications is None:
        raise HTTPException(status_code=404, detail="Notifications not found")
    return db_notifications

@app.put("/notifications/{notification_id}/", response_model=schemas.Notification)
def update_notification(notification_id: int, db: Session = Depends(get_db)):
    db_notification = controllers.update_notification(db, notification_id=notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification


@app.delete("/notifications/{notification_id}/", response_model=schemas.Notification)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    db_notification = controllers.delete_notification(db, notification_id=notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return db_notification

#match functions
@app.post("/users/{user_id}/matches/") #, response_model=schemas.Match
def create_match_for_user(
    user_id: int, match: schemas.MatchCreate, db: Session = Depends(get_db)
):
    return controllers.create_user_match(db=db, match=match, user_id=user_id)

@app.get("/matches/", response_model=list[schemas.Match]) #, response_model=list[schemas.Match]
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches = controllers.get_matches(db, skip=skip, limit=limit)
    return matches

@app.get("/sports/{sport_id}/matches/", response_model=list[schemas.Match])
def read_matches_by_sport(sport_id: int, db: Session = Depends(get_db)):
    db_matches = controllers.get_matches_by_sport(db, sport_id=sport_id)
    if db_matches is None:
        raise HTTPException(status_code=404, detail="Matches not found")
    return db_matches

@app.get("/users/{user_id}/matches/", response_model=list[schemas.Match])
def read_user_matches(user_id: int, db: Session = Depends(get_db)):
    db_matches = controllers.get_user_matches(db, user_id=user_id)
    if db_matches is None:
        raise HTTPException(status_code=404, detail="Matches not found")
    return db_matches

from pydantic import parse_obj_as

@app.websocket("/ws/matches/{user_id}")
async def matches_websocket(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            matches = controllers.get_user_matches(db, user_id=user_id)
            pydantic_matches = parse_obj_as(list[schemas.Match], matches)
            data = [match.dict() for match in pydantic_matches]
            await websocket.send_json(data)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")

@app.get("/matches/{match_id}", response_model=schemas.Match)
def read_match(match_id: int, db: Session = Depends(get_db)):
    db_match = controllers.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

@app.put("/matches/{match_id}/rate")
def update_match_rate(
    match_id: int, 
    rate: float = Query(..., description="Rating for the match"), 
    is_user_created: bool = Query(..., description="Flag indicating if the user created the match"),
    db: Session = Depends(get_db)
):
    return controllers.add_rate_to_match(db=db, match_id=match_id, rate=rate, is_user_created=is_user_created)



@app.put("/matches/{match_id}/users/{user_id}/") #, response_model=schemas.Match
def add_user_to_match(
    match_id: int, user_id: int, db: Session = Depends(get_db)
):
    return controllers.add_user_to_match(db=db, match_id=match_id, user_id=user_id)

@app.put("/matches/{match_id}/status", response_model=schemas.Match)
def change_match_status(
    match_id: int, status: str, db: Session = Depends(get_db)
):
    return controllers.change_match_status(db=db, match_id=match_id, status=status)


class MatchDeleteResponse(BaseModel):
    detail: str

@app.delete("/matches/{match_id}/", response_model=MatchDeleteResponse)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    db_match = controllers.get_match_by_id(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    controllers.delete_match(db, db_match)
    return MatchDeleteResponse(detail="Match deleted successfully")



#sport functions
@app.post("/sports/", response_model=schemas.Sport)
def create_sport(sport: schemas.SportCreate, db: Session = Depends(get_db)):
    return controllers.create_sport(db=db, sport=sport)

@app.get("/sports/", response_model=list[schemas.Sport])
def read_sports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sports = controllers.get_sports(db, skip=skip, limit=limit)
    return sports

@app.delete("/sports/{sport_id}/", response_model=schemas.Sport)
def delete_sport(sport_id: int, db: Session = Depends(get_db)):
    db_sport = controllers.delete_sport(db, sport_id=sport_id)
    if db_sport is None:
        raise HTTPException(status_code=404, detail="Sport not found")
    return db_sport


#level functions
@app.post("/levels/", response_model=schemas.Level)
def create_level(level: schemas.LevelCreate, db: Session = Depends(get_db)):
    return controllers.create_level(db=db, level=level)

@app.get("/levels/", response_model=list[schemas.Level])
def read_levels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    levels = controllers.get_levels(db, skip=skip, limit=limit)
    return levels

@app.delete("/levels/{level_id}/", response_model=schemas.Level)
def delete_level(level_id: int, db: Session = Depends(get_db)):
    db_level = controllers.get_level(db, level_id=level_id)  # Asume que tienes esta función en tus controllers
    if db_level is None:
        raise HTTPException(status_code=404, detail="Level not found")
    controllers.delete_level(db, level_id=level_id)  # Asume que vas a crear esta función en tus controllers
    return db_level


#university functions
@app.get("/universities/", response_model=list[str])
def read_universities(db: Session = Depends(get_db)):
    universities = controllers.get_universities()
    return universities

#city functions
@app.get("/cities/", response_model=list[str])
def read_cities(db: Session = Depends(get_db)):
    cities = controllers.get_cities()
    return cities

#gender functions
@app.get("/genders/", response_model=list[str])
def read_genders(db: Session = Depends(get_db)):
    cities = controllers.get_genders()
    return cities

#get roles
@app.get("/roles/", response_model=list[str])
def read_roles(db: Session = Depends(get_db)):
    roles = controllers.get_roles()
    return roles

#get cities
@app.get("/cities/", response_model=list[str])
def read_cities(db: Session = Depends(get_db)):
    cities = controllers.get_cities()
    return cities

#get courts
@app.get("/courts/", response_model=list[str])
def read_courts(db: Session = Depends(get_db)):
    courts = controllers.get_courts()
    return courts
from datetime import datetime, timezone
import re

# periodic task
def check_and_update_matches():
    db = next(get_db())  # Obtén la sesión de la base de datos
    try:
        matches = db.query(Match).filter(Match.status == 'Pending').all()
        for match in matches:
            # Asumiendo que match.time es una cadena en el formato "HH:MM - HH:MM"
            start_time = re.match(r'(\d{2}:\d{2}) - \d{2}:\d{2}', match.time).group(1)
            match_datetime_str = f'{match.date} {start_time}'
            match_date = datetime.strptime(match_datetime_str, '%d/%m/%Y %H:%M')
            if match_date < datetime.now():
                match.status = 'Out of Date'
                db.commit()
                print(f'Match {match.id} ha sido actualizado a Out of Date')
    except Exception as e:
        print('Error al comprobar los partidos:', e)
    finally:
        db.close()







def run_schedule():
    schedule.every(10).seconds.do(check_and_update_matches)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=run_schedule)
    thread.start()

# Claim endpoint
@app.post("/claims/", response_model=schemas.Claim) #
def create_claim(claim: schemas.ClaimCreate, db: Session = Depends(get_db)):
    return controllers.create_claim(db=db, claim=claim)

@app.get("/claims/", response_model=list[schemas.Claim]) #
def read_claims(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    claims = controllers.get_claims(db, skip=skip, limit=limit)
    return claims

@app.get("/claims/{claim_id}", response_model=schemas.Claim) #
def read_claim(claim_id: int, db: Session = Depends(get_db)):
    db_claim = controllers.get_claim(db, claim_id=claim_id)
    if db_claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return db_claim