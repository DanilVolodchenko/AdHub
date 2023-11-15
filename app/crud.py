from typing import Annotated

from fastapi import HTTPException, security, Depends
from jose import JWTError
from http import HTTPStatus

from sqlalchemy.orm import Session

from app.models import Ad, User, Comment
from app.security import password_hasher, create_password_hash, decode_token
from app.database import SessionLocal, get_db

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """Проверяет пароль."""

    return password_hasher.verify(plain_password, hashed_password)


def create_user(db_session, username: str,
                email: str, password: str, role: str):
    """Создает пользователя."""

    hashed_password = create_password_hash(password)
    db_user = User(username=username, email=email,
                   hashed_password=hashed_password, role=role)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


def get_user_by_username(db_session: SessionLocal, username: str):
    """Получение пользователя по его username."""

    return db_session.query(User).filter(User.username == username).first()


def get_user_by_email(db_session: SessionLocal, email: str):
    """Получение пользователя по его email."""

    return db_session.query(User).filter(User.email == email).first()


# def get_current_user(db_session: Session, token: Annotated[str, Depends(oauth2_scheme)]):
#     """Получение текущего пользователя."""
#
#     try:
#         get_data = decode_token(token)
#     except JWTError:
#         raise HTTPException(detail='Неверный токен!',
#                             status_code=HTTPStatus.NOT_FOUND)
#
#     username = get_data.get('username')
#
#     user = db_session.query(User).filter(User.username == username).first()
#
#     if not user:
#         raise HTTPException(detail='Пользователь не найден!',
#                             status_code=HTTPStatus.NOT_FOUND)
#     return user
def get_current_user(token: str = Depends(oauth2_scheme), db_session: SessionLocal = Depends(get_db)):
    """Получение текущего пользователя."""

    try:
        get_data = decode_token(token)
    except JWTError:
        raise HTTPException(detail='Неверный токен!',
                            status_code=HTTPStatus.NOT_FOUND)

    username = get_data.get('username')

    user = db_session.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(detail='Пользователь не найден!',
                            status_code=HTTPStatus.NOT_FOUND)
    return user


def get_ad(db_session: Session, ad_id: int):
    """Получения объявления по id."""

    ad = db_session.query(Ad).get(ad_id)
    if not ad:
        raise HTTPException(detail='Объявление не найдено!',
                            status_code=HTTPStatus.NOT_FOUND)

    return ad


def get_ads(db_session):
    """Получение списка всех объявлений."""

    return db_session.query(Ad).all()


def create_ad(db_session, title: str, description: str, owner_id: int):
    """Создание объявления."""

    db_ad = Ad(title=title, description=description, owner_id=owner_id)
    db_session.add(db_ad)
    db_session.commit()
    db_session.refresh(db_ad)

    return db_ad


def delete_ad(db_session, ad_id: int, user: User):
    """Удаление объяления."""

    ad = db_session.query(Ad).filter(Ad.id == ad_id).first()
    if ad:
        if ad.owner_id == user.id or user.role == 'admin':
            db_session.delete(ad)
            db_session.commit()
        else:
            raise HTTPException(detail='Не прав на удаление объявления!',
                                status_code=HTTPStatus.BAD_REQUEST)

    else:
        raise HTTPException(detail='Объявление не найдено!',
                            status_code=HTTPStatus.NOT_FOUND)


def update_user_role(db_session: SessionLocal,
                     user_id: int, role: str,
                     current_user_role: str):
    """Изменение роли пользователя только админом."""

    user = db_session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(detail='Такого пользователя не существует!',
                            status_code=HTTPStatus.NOT_FOUND)

    if current_user_role != 'admin' or user.role == 'admin':
        raise HTTPException(detail='Нет прав для этой операции!',
                            status_code=HTTPStatus.NOT_FOUND)

    user.role = role
    db_session.commit()
    db_session.refresh(user)

    return user


def get_comment(db_session: SessionLocal, comment_id):
    """Получает определенный комментарий."""

    comment = db_session.query(Comment).filter(
        Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(detail='Комментарий не найден!',
                            status_code=HTTPStatus.NOT_FOUND)

    return comment


def get_comments(db_session: SessionLocal):
    """Получает все комментарии."""

    return db_session.query(Comment).all()


def create_comment(db_session: SessionLocal, comment: str,
                   user_id: int, ad_id: int):
    """Создание комментариев."""

    ad = db_session.query(Ad).get(ad_id)
    if not ad:
        raise HTTPException(detail='Объявление не найдено!',
                            status_code=HTTPStatus.NOT_FOUND)

    db_comment = Comment(text=comment, owner_id=user_id, ad_id=ad_id)
    db_session.add(db_comment)
    db_session.commit()
    db_session.refresh(db_comment)

    return db_comment


def delete_comment(db_session: SessionLocal, comment_id: int, user_id: int):
    """Удаление комментария."""

    comment = db_session.query(Comment).filter(
        Comment.id == comment_id).first()
    user = db_session.query(User).filter(User.id == user_id).first()

    if comment:
        if comment.user.id == user.id or user.role == 'admin':
            db_session.delete(comment)
            db_session.commit()
        else:
            raise HTTPException(detail='Нет прав на удаление комментария!',
                                status_code=HTTPStatus.BAD_REQUEST)
    else:
        raise HTTPException(detail='Комментрарий не найден!',
                            status_code=HTTPStatus.NOT_FOUND)
