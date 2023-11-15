from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import crud, schemas, database, security

router = APIRouter(
    tags=['auth'],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Регистрация пользователя."""

    db_user_by_username = crud.get_user_by_username(db, user.username)
    db_user_by_email = crud.get_user_by_email(db, user.email)

    if db_user_by_username or db_user_by_email:
        raise HTTPException(detail='Такой пользователь уже зарегистрирован!',
                            status_code=HTTPStatus.BAD_REQUEST)

    return crud.create_user(db, **user.model_dump())


@router.post('/token', response_model=schemas.TokenRead)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(database.get_db)):
    """Аутентификация и получение токена."""

    user = crud.get_user_by_username(db, form_data.username)
    if not form_data or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(detail='Неверный username или password!',
                            status_code=HTTPStatus.BAD_REQUEST)

    token = security.create_access_token(user)

    return JSONResponse(content={'access_token': token, 'token_type': 'bearer'})
