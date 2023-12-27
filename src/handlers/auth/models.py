from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)
    tg_id = Column('tg_id', Integer, index=True)
    email = Column('email', String)
    password_hash = Column('password_hash', String)

    sessions = relationship('UserSession', back_populates='user', cascade='all,delete')

    __table_args__ = (
        UniqueConstraint('tg_id', 'email', name='tgid_email_unique'),
    )


class UserSession(Base):
    __tablename__ = 'sessions'

    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', ForeignKey('users.id'))
    tg_id = Column('tg_id', Integer, unique=True)

    user = relationship('User', back_populates='sessions')
