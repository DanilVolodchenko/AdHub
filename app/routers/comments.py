from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix='/comments',
    tags=['comments'],
    responses={404: {"description": "Not found"}},
)


@router.get('/', response_model=list[schemas.CommentRead])
def get_comments(db: Session = Depends(get_db)):
    """Возвращает список комментариев."""

    return crud.get_comments(db)


@router.get('/{comment_id}', response_model=schemas.CommentRead)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Возвращает определенный комментарий"""

    return crud.get_comment(db, comment_id)


@router.post('/{ad_id}', response_model=schemas.CommentRead)
def create_comment(ad_id: int,
                   comment: schemas.CommentCreate,
                   current_user: schemas.User = Depends(crud.get_current_user),
                   db: Session = Depends(get_db)):
    """Создание комментария к объявлению."""

    comment = crud.create_comment(db, comment.text, current_user.id, ad_id)

    return comment


@router.delete('/{comment_id}')
def delete_comment(comment_id: int,
                   current_user: schemas.User = Depends(crud.get_current_user),
                   db: Session = Depends(get_db)):
    """Удаление комментария."""

    crud.delete_comment(db, comment_id, current_user.id)

    return JSONResponse(content={'detail': 'Комментарий успешно удален!'},
                        status_code=HTTPStatus.OK)
