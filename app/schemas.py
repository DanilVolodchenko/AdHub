from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class TitleEnum(str, Enum):
    sell = 'Продажа'
    buy = 'Покупка'
    service = 'Оказание услуг'


class RoleEnum(str, Enum):
    admin = 'admin'
    user = 'user'


class UserBase(BaseModel):
    username: str
    email: EmailStr


class AdBase(BaseModel):
    title: str = Field(default=TitleEnum.sell)
    description: str = Field(min_length=5, max_length=500)


class CommentBase(BaseModel):
    text: str = Field(min_length=5, max_length=300)


class User(UserBase):
    role: RoleEnum
    id: int


class Ad(AdBase):
    id: int


class Comment(CommentBase):
    id: int


class UserRead(UserBase):
    role: RoleEnum
    id: int
    ads: list[Ad] = []
    comments: list[Comment] = []


class UserCreate(UserBase):
    password: str


class Token(BaseModel):
    username: str
    password: str


class TokenRead(BaseModel):
    token_type: str
    token: str


class AdRead(AdBase):
    id: int
    owner: User


class AdCreate(AdBase):
    pass


class CommentRead(CommentBase):
    id: int
    user: User
    ad: Ad


class CommentCreate(CommentBase):
    pass
