from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, Form, Body, Query
from sqlalchemy.orm import Session
import base64

import crud
import models
import schemas
import requests
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


@app.delete("/users/", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user_id)


@app.put("/users/", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UpdateUser, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.update_user(db, user, db_user)


@app.patch("/users/")
def update_user_password(user_id: int, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.update_user(db, password, db_user)


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_item


@app.delete("/items/", status_code=204, responses={404: {"detail": "Mal"}})
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_item(db, item_id)


@app.post("/", status_code=200, description="Borra el fondo de 4 imagenes y saca las medidas de la persona")
def background(sex: schemas.sexStatus = Query(title="sexo", description="sexo del usuario"),
               height: int = Query(title="altura", description="altura del usuario", gt=0),
               img: schemas.Image_64 = Body(description="Las imagenes")):
    # validar usuario
    data = {
        "username": "demo@demo.com",
        "password": "password"
    }
    ids = []
    response = requests.post("https://pre.app.aitaca.io/users/login", data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": "Bearer " + access_token}
    # put
    data = {
        "height": height,
        "sex": sex
    }
    res = requests.put("https://pre.app.aitaca.io/users/", json=data, headers=headers)
    # front_down
    decoded_image = base64.b64decode(img.front_down)
    files = {"original_image": ("front_down.jpg", decoded_image, "image/jpg")}
    response = requests.post("https://pre.app.aitaca.io/background/removal", files=files, headers=headers)
    ids.append(response.json()["uuid"])
    # front_up
    decoded_image = base64.b64decode(img.front_up)
    files = {"original_image": ("front_up.jpg", decoded_image, "image/jpg")}
    response = requests.post("https://pre.app.aitaca.io/background/removal", files=files, headers=headers)
    ids.append(response.json()["uuid"])
    # side_down
    decoded_image = base64.b64decode(img.side_down)
    files = {"original_image": ("side_down.jpg", decoded_image, "image/jpg")}
    response = requests.post("https://pre.app.aitaca.io/background/removal", files=files, headers=headers)
    ids.append(response.json()["uuid"])
    # side_up
    decoded_image = base64.b64decode(img.side_up)
    files = {"original_image": ("side_up.jpg", decoded_image, "image/jpg")}
    response = requests.post("https://pre.app.aitaca.io/background/removal", files=files, headers=headers)
    ids.append(response.json()["uuid"])
    data = {
        "front_down": ids[0],
        "front_up": ids[1],
        "side_down": ids[2],
        "side_up": ids[3]
    }
    params = {
        "height": height
    }
    res = requests.post("https://pre.app.aitaca.io/measurements/ia", params=params, json=data, headers=headers)
    return res.json()

