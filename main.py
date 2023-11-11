from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from crud import (get_user_by_username, create_user, verify_password, get_current_user, create_ad, get_ads, get_ad,
                  delete_ad, update_user_role, get_comment, get_comments, create_comment, delete_comment)
from database import SessionLocal
from security import create_access_token
from schemas import AdCreateSchema, UserCreateSchema, GetTokenSchema, AdReadSchema, RoleEnum, CommentReadSchema, \
    CommentCreateSchema
from exceptions import UpdateRoleError, TokenError

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    """Регистрация пользователя."""

    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Такой пользователь уже зарегистрирован!')

    user = create_user(db, user.username, user.email, user.password, user.role)
    return {'username': user.username, 'email': user.email}


@app.post('/token', response_model=GetTokenSchema)
def login(username: str, password: str, db: Session = Depends(get_db)):
    """Аутентификация и получение токена."""

    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return JSONResponse(content='Неверные данные', status_code=HTTPStatus.UNAUTHORIZED)

    token = create_access_token(user)

    response = JSONResponse(content={'token_type': 'jwt', 'token': token})

    return response


@app.get('/users/me')
def read_users_me(token: str, db: Session = Depends(get_db)):
    """Получение текущего пользователя."""

    try:
        current_user = get_current_user(db, token)
    except TokenError:
        return JSONResponse(content='Неверный токен!', status_code=HTTPStatus.UNAUTHORIZED)

    return {'status_code': HTTPStatus.OK, 'user': current_user}


@app.patch('/users/{user_id}')
def update_user(user_id: int, token: str, db: Session = Depends(get_db)):
    """Изменение роли пользователя."""

    try:
        current_user = get_current_user(db, token)
    except TokenError:
        return JSONResponse(content='Неверный токен!', status_code=HTTPStatus.UNAUTHORIZED)

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
        return JSONResponse(content='Объявление не найдено!')

    return ads


@app.post('/ads', response_model=AdCreateSchema)
def ad_create(token: str, ad: AdCreateSchema, db: Session = Depends(get_db)):
    """Создание объявления."""

    try:
        current_user = get_current_user(db, token)
    except TokenError:
        return JSONResponse(content='Неверный токен!', status_code=HTTPStatus.UNAUTHORIZED)

    create_ad(db, ad.title, ad.description, owner_id=current_user.id)

    return JSONResponse(content='Объявление успешно создано!', status_code=HTTPStatus.CREATED)


@app.delete('/ads/{ad_id}')
def delete_certain_ad(ad_id: int, token: str, db: Session = Depends(get_db)):
    """Удаляет определенное объявление."""

    try:
        current_user = get_current_user(db, token)
    except TokenError:
        return JSONResponse(content='Неверный токен!', status_code=HTTPStatus.UNAUTHORIZED)
    try:
        delete_ad(db, ad_id, current_user)
    except HTTPException:
        return JSONResponse(content='Нет прав на удаление объявления!', status_code=HTTPStatus.UNAUTHORIZED)

    return JSONResponse(content='Объявление успешно удалено!', status_code=HTTPStatus.OK)


@app.get('/comments', response_model=list[CommentReadSchema])
def get_list_of_comments(db: Session = Depends(get_db)):
    return get_comments(db)


@app.get('/comments/{comment_id}', response_model=CommentReadSchema)
def get_certain_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = get_comment(db, comment_id)
    if not comment:
        return JSONResponse(content='Комментарий не найден!')

    return comment


@app.post('/comments/{ad_id}')
def comment_create(ad_id: int, token: str, comment: CommentCreateSchema, db: Session = Depends(get_db)):
    """Создание комментария к объявлению."""

    try:
        current_user = get_current_user(db, token)
        create_comment(db, comment.text, current_user.id, ad_id)

    except ValueError:
        return JSONResponse(content='Объявление не найдено!', status_code=HTTPStatus.CREATED)
    except TokenError:
        return JSONResponse(content='Неверный токен!', status_code=HTTPStatus.UNAUTHORIZED)

    return JSONResponse(content='Комментарий успешно создан!', status_code=HTTPStatus.CREATED)


@app.delete('/comments/{comment_id}')
def comment_delete(comment_id: int, token: str, db: Session = Depends(get_db)):
    """Удаление комментария."""

    try:
        current_user = get_current_user(db, token)
    except TokenError:
        return JSONResponse(content='Неверный токен!', status_code=HTTPStatus.UNAUTHORIZED)

    delete_comment(db, comment_id, current_user.id)

    return JSONResponse(content='Комментарий успешно удален!', status_code=HTTPStatus.OK)
