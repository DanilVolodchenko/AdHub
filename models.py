from sqlalchemy import Column, MetaData, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from database import Base
from schemas import RoleEnum

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
    comments = relationship('Comment', back_populates='owner')


class Ad(Base):
    """Таблица объявлений."""

    __tablename__ = 'ads'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='ads')
    comment = relationship('Comment', back_populates='ads')


class Comment(Base):
    """Таблица комментариев,"""

    __tablename__ = 'comments'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    ad_id = Column(Integer, ForeignKey('ads.id'))

    owner = relationship('User', back_populates='comments')
    ad = relationship('Ad', back_populates='comments')
