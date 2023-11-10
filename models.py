from sqlalchemy import Column, MetaData, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

metadata = MetaData()


class User(Base):
    """Таблица для юзера."""
    __tablename__ = "users"
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    ads = relationship('Ad', back_populates='owner')


class Ad(Base):
    """Таблица объявлений."""
    __tablename__ = "ads"
    metadata = metadata

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship('User', back_populates='ads')
