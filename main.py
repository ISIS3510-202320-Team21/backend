from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#user functions
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#item functions
@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

#image functions
@app.post("/users/{user_id}/images/", response_model=schemas.Image)
def create_image_for_user(
    user_id: int, image: schemas.ImageCreate, db: Session = Depends(get_db)
):
    return crud.create_user_image(db=db, image=image, user_id=user_id)

@app.get("/images/", response_model=list[schemas.Image])
def read_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    images = crud.get_images(db, skip=skip, limit=limit)
    return images

#notification functions
@app.post("/users/{user_id}/notifications/", response_model=schemas.Notification)
def create_notification_for_user(
    user_id: int, notification: schemas.NotificationCreate, db: Session = Depends(get_db)
):
    return crud.create_user_notification(db=db, notification=notification, user_id=user_id)

@app.get("/notifications/", response_model=list[schemas.Notification])
def read_notifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notifications = crud.get_notifications(db, skip=skip, limit=limit)
    return notifications

@app.get("/users/{user_id}/notifications/", response_model=list[schemas.Notification])
def read_user_notifications(user_id: int, db: Session = Depends(get_db)):
    db_notifications = crud.get_user_notifications(db, user_id=user_id)
    if db_notifications is None:
        raise HTTPException(status_code=404, detail="Notifications not found")
    return db_notifications

#match functions
@app.post("/users/{user_id}/matches/", response_model=schemas.Match)
def create_match_for_user(
    user_id: int, match: schemas.MatchCreate, db: Session = Depends(get_db)
):
    return crud.create_match_for_user(db=db, match=match, user_id=user_id)

@app.get("/matches/", response_model=list[schemas.Match])
def read_matches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    matches = crud.get_matches(db, skip=skip, limit=limit)
    return matches

# @app.get("/users/{user_id}/matches/", response_model=list[schemas.Match])
# def read_user_matches(user_id: int, db: Session = Depends(get_db)):
#     db_matches = crud.get_user_matches(db, user_id=user_id)
#     if db_matches is None:
#         raise HTTPException(status_code=404, detail="Matches not found")
#     return db_matches

@app.put("/matches/{match_id}/rate/", response_model=schemas.Match)
def update_match_rate(
    match_id: int, rate: str, db: Session = Depends(get_db)
):
    return crud.add_rate_to_match(db=db, match_id=match_id, rate=rate)

@app.put("/matches/{match_id}/users/{user_id}/", response_model=schemas.Match)
def add_user_to_match(
    match_id: int, user_id: int, db: Session = Depends(get_db)
):
    return crud.add_user_to_match(db=db, match_id=match_id, user_id=user_id)

#sport functions
@app.post("/sports/", response_model=schemas.Sport)
def create_sport(sport: schemas.SportCreate, db: Session = Depends(get_db)):
    return crud.create_sport(db=db, sport=sport)

@app.get("/sports/", response_model=list[schemas.Sport])
def read_sports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sports = crud.get_sports(db, skip=skip, limit=limit)
    return sports

#level functions
@app.post("/levels/", response_model=schemas.Level)
def create_level(level: schemas.LevelCreate, db: Session = Depends(get_db)):
    return crud.create_level(db=db, level=level)

@app.get("/levels/", response_model=list[schemas.Level])
def read_levels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    levels = crud.get_levels(db, skip=skip, limit=limit)
    return levels