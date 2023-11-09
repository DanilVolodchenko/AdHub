from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = MetaData()


class User(Base):
    """Таблица пользователей."""

    __tablename__ = 'users'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True),
    password = Column(String, nullable=False),
    created_at = Column(TIMESTAMP, default=datetime.utcnow),

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship('Role', back_populates='user')
    ads = relationship('Ad', back_populates='user')
    comments = relationship("Comment", back_populates="author")


class Role(Base):
    """Таблица с ролями пользователей."""

    __tablename__ = 'roles'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False),
    permission = Column(JSON)


class Ad(Base):
    """Таблица с объявлениями."""

    __tablename__ = 'ads'
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='ads')
    comments = relationship('Comment', back_populates='ad')


class Comment(Base):
    """Таблица с комментариями."""

    __tablename__ = 'comments'
    metadata = metadata

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    ad_id = Column(Integer, ForeignKey('ads.id'))

    author = relationship('User', back_populates='comments')
    ad = relationship("Ad", back_populates="comments")
