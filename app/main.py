from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, security
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import crud, schemas
from app.database import SessionLocal
from app.security import create_access_token
from app.database import get_db

app = FastAPI()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя."""

    db_user_by_username = crud.get_user_by_username(db, user.username)
    db_user_by_email = crud.get_user_by_email(db, user.email)

    if db_user_by_username or db_user_by_email:
        raise HTTPException(detail='Такой пользователь уже зарегистрирован!',
                            status_code=HTTPStatus.BAD_REQUEST)

    return crud.create_user(db, **user.model_dump())


@app.post('/token', response_model=schemas.TokenRead)
def login(form_data: Annotated[security.OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    """Аутентификация и получение токена."""

    user = crud.get_user_by_username(db, form_data.username)
    if not form_data or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(detail='Неверный username или password!',
                            status_code=HTTPStatus.BAD_REQUEST)

    token = create_access_token(user)

    return JSONResponse(content={'access_token': token, 'token_type': 'bearer'})


@app.get('/users/me', response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(crud.get_current_user)):
    # token: Annotated[str, Depends(crud.oauth2_scheme)], db: Session = Depends(get_db)):
    """Получение текущего пользователя."""

    # current_user = crud.get_current_user(db, token)

    return current_user


@app.patch('/users/{user_id}', response_model=schemas.UserRead)
def update_user(user_id: int,
                current_user: schemas.User = Depends(crud.get_current_user),
                db: Session = Depends(get_db)):
    """Изменение роли пользователя."""

    user = crud.update_user_role(db, user_id, schemas.RoleEnum.admin, current_user.role)

    return user


@app.get('/ads', response_model=list[schemas.AdRead])
def read_ads(db: Session = Depends(get_db)):
    """Возвращает список объявлений."""

    return crud.get_ads(db)


@app.get('/ads/{ad_id}', response_model=schemas.AdRead)
def read_ad(ad_id: int, db: Session = Depends(get_db)):
    """Возвращает определенное объявление."""

    ad = crud.get_ad(db, ad_id)

    return ad


@app.post('/ads', response_model=schemas.AdRead)
def create_ad(ad: schemas.AdCreate, current_user: schemas.User = Depends(crud.get_current_user),
              db: Session = Depends(get_db)):
    """Создание объявления."""

    ad = crud.create_ad(db, ad.title, ad.description, owner_id=current_user.id)

    return ad


@app.delete('/ads/{ad_id}')
def delete_ad(ad_id: int, current_user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(get_db)):
    """Удаляет определенное объявление."""

    crud.delete_ad(db, ad_id, current_user)

    return JSONResponse(content={'detail': 'Объявление успешно удалено!'},
                        status_code=HTTPStatus.OK)


@app.get('/comments', response_model=list[schemas.CommentRead])
def get_comments(db: Session = Depends(get_db)):
    """Возвращает список комментариев."""

    return crud.get_comments(db)


@app.get('/comments/{comment_id}', response_model=schemas.CommentRead)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Возвращает определенный комментарий"""

    return crud.get_comment(db, comment_id)


@app.post('/comments/{ad_id}', response_model=schemas.CommentRead)
def create_comment(ad_id: int,
                   comment: schemas.CommentCreate,
                   current_user: schemas.User = Depends(crud.get_current_user),
                   db: Session = Depends(get_db)):
    """Создание комментария к объявлению."""

    comment = crud.create_comment(db, comment.text, current_user.id, ad_id)

    return comment


@app.delete('/comments/{comment_id}')
def delete_comment(comment_id: int,
                   current_user: schemas.User = Depends(crud.get_current_user),
                   db: Session = Depends(get_db)):
    """Удаление комментария."""

    crud.delete_comment(db, comment_id, current_user.id)

    return JSONResponse(content={'detail': 'Комментарий успешно удален!'},
                        status_code=HTTPStatus.OK)
