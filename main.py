from http import HTTPStatus
from fastapi import Depends, FastAPI, HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from crud import (get_user_by_username, create_user, verify_password, get_current_user, create_ad, get_ads, get_ad,
                  delete_ad)
from database import SessionLocal
from security import create_access_token
from schemas import AdSchema

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/register")
def register(username: str, email: EmailStr, password: str, db: Session = Depends(get_db)):
    """Регистрация пользователя."""

    db_user = get_user_by_username(db, username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username already registered")

    user = create_user(db, username, email, password)
    return {"username": user.username, "email": user.email}


@app.post("/token")
def login(username: str, password: str, db: Session = Depends(get_db)):
    """Аутентификация и получение токена."""

    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return JSONResponse(content='Invalid credentials', status_code=HTTPStatus.UNAUTHORIZED)

    token = create_access_token(user)

    response = JSONResponse(content={'token_type': 'jwt', 'token': token})
    response.set_cookie("access_token", token, httponly=True)

    return response


@app.get('/users/me')
def read_users_me(token: str, db: Session = Depends(get_db)):
    current_user = get_current_user(db, token)
    return {"user": current_user}


@app.get('/ads')
def get_list_of_ads(db: Session = Depends(get_db)):
    """Возвращает список объявлений."""

    return get_ads(db)


@app.post('/ads/{ad_id}')
def create(ad: AdSchema, db: Session = Depends(get_db)):
    """Создание объявления."""

    current_user = get_current_user(db, ad.token)
    create_ad(db, ad.title, ad.description, owner_id=current_user.id)

    return JSONResponse(content='Ad successfully create!', status_code=HTTPStatus.CREATED)


@app.get('/ads/{ad_id}')
def get_certain_ad(ad_id: int, db: Session = Depends(get_db)):
    """Возвращает определенное объявление."""

    return get_ad(db, ad_id)


@app.delete('/ads/{ad_id}')
def delete_certain_ad(ad_id: int, db: Session = Depends(get_db)):
    """Удаляет определенное объявление."""

    delete_ad(db, ad_id)
    return JSONResponse(content='Ad successfully deleted', status_code=HTTPStatus.OK)
