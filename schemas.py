from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class TitleEnum(str, Enum):
    sell = 'Продажа'
    buy = 'Покупка'
    service = 'Оказание услуг'


class RoleEnum(str, Enum):
    admin = 'admin'
    user = 'user'


class UserRegisterSchema(BaseModel):
    id: int
    username: str
    email: str
    role: RoleEnum


class UserReadSchema(BaseModel):
    id: int
    username: str
    email: str
    hash_password: str = 'asdf'
    role: RoleEnum = RoleEnum.user


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.user


class AdCreateSchema(BaseModel):
    title: TitleEnum = Field(default=TitleEnum.sell)
    description: str = Field(min_length=5, max_length=250)


class AdReadSchema(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int


class GetTokenSchema(BaseModel):
    username: str
    password: str


class CommentReadSchema(BaseModel):
    id: int
    text: str
    owner_id: int
    ad_id: int


class CommentCreateSchema(BaseModel):
    text: str
