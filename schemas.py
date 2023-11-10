from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class TitleEnum(str, Enum):
    sell = 'Продажа'
    buy = 'Покупка'
    service = 'Оказание услуг'


class AdSchema(BaseModel):
    token: str
    title: TitleEnum = Field(default=TitleEnum.sell)
    description: str = Field(min_length=5, max_length=250)


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str


class TokenSchema(BaseModel):
    username: str
    hashed_password: str
