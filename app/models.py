from sqlalchemy import Column, ForeignKey, MetaData, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.schemas import RoleEnum

metadata = MetaData()


class User(Base):
    """Таблица для юзера."""

    __tablename__ = 'users'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=RoleEnum.user, nullable=True)

    ads = relationship('Ad', back_populates='owner')
    comments = relationship('Comment', back_populates='user')

    @property
    def is_admin(self):
        return self.role == 'admin'


class Ad(Base):
    """Таблица объявлений."""

    __tablename__ = 'ads'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='ads')
    comments = relationship('Comment', back_populates='ad')


class Comment(Base):
    """Таблица комментариев."""

    __tablename__ = 'comments'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    ad_id = Column(Integer, ForeignKey('ads.id'))

    user = relationship('User', back_populates='comments')
    ad = relationship('Ad', back_populates='comments')
