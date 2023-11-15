from passlib.context import CryptContext
from jose import jwt

from app.models import User
from config import JWT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

JWT_SECRET = JWT_SECRET
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_password_hash(password):
    """Создает хэш пароля."""

    return password_hasher.hash(password)


def create_access_token(user: User):
    """Создает токен."""
    try:
        payload = {
            'username': user.username,
            'email': user.email
        }
        return jwt.encode(payload, key=JWT_SECRET, algorithm=ALGORITHM)
    except Exception as ex:
        raise ex


def decode_token(token):
    return jwt.decode(token, key=JWT_SECRET, algorithms=ALGORITHM)
