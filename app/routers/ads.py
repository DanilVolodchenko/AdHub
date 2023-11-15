from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix='/ads',
    tags=['ads'],
    responses={404: {"description": "Not found"}},
)


@router.get('/', response_model=list[schemas.AdRead])
def read_ads(db: Session = Depends(get_db)):
    """Возвращает список объявлений."""

    return crud.get_ads(db)


@router.get('/{ad_id}', response_model=schemas.AdRead)
def read_ad(ad_id: int, db: Session = Depends(get_db)):
    """Возвращает определенное объявление."""

    ad = crud.get_ad(db, ad_id)

    return ad


@router.post('', response_model=schemas.AdRead)
def create_ad(ad: schemas.AdCreate, current_user: schemas.User = Depends(crud.get_current_user),
              db: Session = Depends(get_db)):
    """Создание объявления."""

    ad = crud.create_ad(db, ad.title, ad.description, owner_id=current_user.id)

    return ad


@router.delete('/{ad_id}')
def delete_ad(ad_id: int, current_user: schemas.User = Depends(crud.get_current_user), db: Session = Depends(get_db)):
    """Удаляет определенное объявление."""

    crud.delete_ad(db, ad_id, current_user)

    return JSONResponse(content={'detail': 'Объявление успешно удалено!'},
                        status_code=HTTPStatus.OK)
