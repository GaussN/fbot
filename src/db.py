from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DB_CONNECT_STRING

engine = create_engine(DB_CONNECT_STRING)
Session = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass
