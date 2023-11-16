from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {"description": "Not found"}},
)


@router.get('/me', response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(crud.get_current_user)):
    """Получение текущего пользователя."""

    return current_user


@router.patch('/{user_id}', response_model=schemas.UserRead)
def update_user(user_id: int,
                current_user: schemas.User = Depends(crud.get_current_user),
                db: Session = Depends(get_db)):
    """Изменение роли пользователя."""

    user = crud.update_user_role(db, user_id, schemas.RoleEnum.admin, current_user)

    return user
