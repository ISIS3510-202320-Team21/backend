from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import controllers, models, schemas
from fastapi.middleware.cors import CORSMiddleware
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
    db: Session = Depends(get_db)
):
    return controllers.add_rate_to_match(db=db, match_id=match_id, rate=rate)



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

#sport functions
@app.post("/sports/", response_model=schemas.Sport)
def create_sport(sport: schemas.SportCreate, db: Session = Depends(get_db)):
    return controllers.create_sport(db=db, sport=sport)

@app.get("/sports/", response_model=list[schemas.Sport])
def read_sports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sports = controllers.get_sports(db, skip=skip, limit=limit)
    return sports

#level functions
@app.post("/levels/", response_model=schemas.Level)
def create_level(level: schemas.LevelCreate, db: Session = Depends(get_db)):
    return controllers.create_level(db=db, level=level)

@app.get("/levels/", response_model=list[schemas.Level])
def read_levels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    levels = controllers.get_levels(db, skip=skip, limit=limit)
    return levels

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