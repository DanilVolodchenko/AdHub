from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from crud import (get_user_by_username, create_user, verify_password, get_current_user, create_ad, get_ads, get_ad,
                  delete_ad, update_user_role)
from database import SessionLocal
from security import create_access_token
from schemas import AdCreateSchema, UserCreateSchema, GetTokenSchema, AdReadSchema, RoleEnum
from exceptions import UpdateRoleError

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


@app.post("/register")  # , response_model=UserSchema)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    """Регистрация пользователя."""

    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Такой пользователь уже зарегистрирован!")

    user = create_user(db, user.username, user.email, user.password, user.role)
    return {"username": user.username, "email": user.email}


@app.post("/token", response_model=GetTokenSchema)
def login(username: str, password: str, db: Session = Depends(get_db)):
    """Аутентификация и получение токена."""

    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return JSONResponse(content='Invalid credentials', status_code=HTTPStatus.UNAUTHORIZED)

    token = create_access_token(user)

    response = JSONResponse(content={'token_type': 'jwt', 'token': token})

    return response


@app.get('/users/me')
def read_users_me(token: str, db: Session = Depends(get_db)):
    """Получение текущего пользователя."""

    current_user = get_current_user(db, token)

    return {'status_code': HTTPStatus.OK, "user": current_user}


@app.patch('/users/{user_id}')
def update_user(user_id: int, token: str, db: Session = Depends(get_db)):
    """Изменение роли пользователя."""

    current_user = get_current_user(db, token)
    if current_user.role != 'admin':
        return JSONResponse(content='Нет прав для этой операции!', status_code=HTTPStatus.BAD_REQUEST)

    try:
        user = update_user_role(db, user_id, role=RoleEnum.admin)
        if not user:
            return JSONResponse(content='Такого пользователя не существует!', status_code=HTTPStatus.NOT_FOUND)

        return JSONResponse(content=f'Изменение роль пользователя {user.username} прошло успешно!',
                            status_code=HTTPStatus.OK)

    except UpdateRoleError:
        return JSONResponse(content='Нет прав для этой операции!', status_code=HTTPStatus.BAD_REQUEST)


@app.get('/ads', response_model=list[AdReadSchema])
def read_list_of_ads(db: Session = Depends(get_db)):
    """Возвращает список объявлений."""

    return get_ads(db)


@app.get('/ads/{ad_id}', response_model=AdReadSchema)
def read_certain_ad(ad_id: int, db: Session = Depends(get_db)):
    """Возвращает определенное объявление."""

    ads = get_ad(db, ad_id)
    if not ads:
        return JSONResponse(content='Такого объявления нет!')

    return ads


@app.post('/ads', response_model=AdCreateSchema)
def ad_create(ad: AdCreateSchema, db: Session = Depends(get_db)):
    """Создание объявления."""

    current_user = get_current_user(db, ad.token)
    create_ad(db, ad.title, ad.description, owner_id=current_user.id)

    return JSONResponse(content='Объявление успешно создано!', status_code=HTTPStatus.CREATED)


@app.delete('/ads/{ad_id}')
def delete_certain_ad(ad_id: int, db: Session = Depends(get_db)):
    """Удаляет определенное объявление."""

    delete_ad(db, ad_id)

    return JSONResponse(content='Объявление успешно удалено!', status_code=HTTPStatus.OK)



