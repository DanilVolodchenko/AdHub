from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.crud import (get_user_by_username, create_user, verify_password,
                      get_current_user, create_ad, get_ads, get_ad,
                      delete_ad, update_user_role, get_comment, get_comments,
                      create_comment, delete_comment)
from app.database import SessionLocal
from app.security import create_access_token
from app.schemas import (AdCreateSchema, UserCreateSchema, GetTokenSchema,
                         AdReadSchema, RoleEnum, CommentReadSchema,
                         CommentCreateSchema, UserReadSchema, UserRegisterSchema,
                         TokenSchema)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=UserRegisterSchema)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    """Регистрация пользователя."""

    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(detail='Такой пользователь уже зарегистрирован!',
                            status_code=HTTPStatus.BAD_REQUEST)

    return create_user(db, user.username, user.email, user.password, user.role)


@app.post('/token', response_model=GetTokenSchema)
def login(user: TokenSchema, db: Session = Depends(get_db)):
    """Аутентификация и получение токена."""

    db_user = get_user_by_username(db, user.username)
    if not user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(detail='Неверный username или password!',
                            status_code=HTTPStatus.BAD_REQUEST)

    token = create_access_token(db_user)

    return JSONResponse(content={'token_type': 'jwt', 'access_token': token})


@app.get('/users/me', response_model=UserReadSchema)
def read_users_me(token: str, db: Session = Depends(get_db)):
    """Получение текущего пользователя."""

    current_user = get_current_user(db, token)

    return current_user


@app.patch('/users/{user_id}', response_model=UserReadSchema)
def update_user(user_id: int, token: str, db: Session = Depends(get_db)):
    """Изменение роли пользователя."""

    current_user = get_current_user(db, token)
    user = update_user_role(db, user_id, RoleEnum.admin, current_user.role)

    return user


@app.get('/ads', response_model=list[AdReadSchema])
def read_list_of_ads(db: Session = Depends(get_db)):
    """Возвращает список объявлений."""

    return get_ads(db)


@app.get('/ads/{ad_id}', response_model=AdReadSchema)
def read_certain_ad(ad_id: int, db: Session = Depends(get_db)):
    """Возвращает определенное объявление."""

    ad = get_ad(db, ad_id)

    return ad


@app.post('/ads', response_model=AdReadSchema)
def ad_create(token: str, ad: AdCreateSchema, db: Session = Depends(get_db)):
    """Создание объявления."""

    current_user = get_current_user(db, token)
    ad = create_ad(db, ad.title, ad.description, owner_id=current_user.id)

    return ad


@app.delete('/ads/{ad_id}')
def delete_certain_ad(ad_id: int, token: str, db: Session = Depends(get_db)):
    """Удаляет определенное объявление."""

    current_user = get_current_user(db, token)
    delete_ad(db, ad_id, current_user)

    return JSONResponse(content={'detail': 'Объявление успешно удалено!'},
                        status_code=HTTPStatus.OK)


@app.get('/comments', response_model=list[CommentReadSchema])
def get_list_of_comments(db: Session = Depends(get_db)):
    return get_comments(db)


@app.get('/comments/{comment_id}', response_model=CommentReadSchema)
def get_certain_comment(comment_id: int, db: Session = Depends(get_db)):
    """Возвращает определенный комментарий"""

    return get_comment(db, comment_id)


@app.post('/comments/{ad_id}', response_model=CommentReadSchema)
def comment_create(ad_id: int, token: str,
                   comment: CommentCreateSchema,
                   db: Session = Depends(get_db)):
    """Создание комментария к объявлению."""

    current_user = get_current_user(db, token)
    comment = create_comment(db, comment.text, current_user.id, ad_id)

    return comment


@app.delete('/comments/{comment_id}')
def comment_delete(comment_id: int, token: str, db: Session = Depends(get_db)):
    """Удаление комментария."""

    current_user = get_current_user(db, token)

    delete_comment(db, comment_id, current_user.id)

    return JSONResponse(content={'detail': 'Комментарий успешно удален!'},
                        status_code=HTTPStatus.OK)
