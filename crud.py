from fastapi import HTTPException

from models import Ad, User
from security import password_hasher, create_password_hash, decode_token


def verify_password(plain_password, hashed_password):
    """Проверяет пароль."""

    return password_hasher.verify(plain_password, hashed_password)


def create_user(db_session, username: str, email: str, password: str):
    """Создает пользователя."""

    hashed_password = create_password_hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


def get_user_by_username(db_session, username: str):
    """Получение пользователя по его username."""

    return db_session.query(User).filter(User.username == username).first()


def get_user_by_id(db_session, user_id: int):
    """Получение пользователя по id."""

    return db_session.query(User).filter(User.id == user_id).first()


def get_current_user(db_session, token):
    """Получение текущего пользователя."""

    get_data = decode_token(token)
    username = get_data.get('username')
    if not username:
        return {'status_code': 404, 'detail': 'Could not validate credentials'}
    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        return {'status_code': 404, 'detail': 'Could not validate credentials'}
    return user


# Функция для создания объявления
def create_ad(db_session, title: str, description: str, owner_id: int):
    """Создание объявления."""
    db_ad = Ad(title=title, description=description, owner_id=owner_id)
    db_session.add(db_ad)
    db_session.commit()
    db_session.refresh(db_ad)
    return db_ad


def get_ad(db_session, ad_id: int):
    """Получения объявления по id."""

    return db_session.query(Ad).filter(Ad.id == ad_id).first()


def get_ads(db_session):
    """Получение списка всех объявлений."""

    return db_session.query(Ad).all()


def delete_ad(db_session, ad_id: int):
    """Удаление объяления."""

    ad = db_session.query(Ad).filter(Ad.id == ad_id).first()

    if ad:
        db_session.delete(ad)
        db_session.commit()

    else:
        raise HTTPException(status_code=404, detail="Ad not found")
