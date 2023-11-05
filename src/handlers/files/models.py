from pathlib import Path
from os import getenv
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime,  UniqueConstraint

from db import Base


class File(Base):
    __tablename__ = 'files'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    filename = Column('filename', String(50), nullable=False, index=True)
    user_id = Column('userid', Integer, nullable=False)
    hash = Column('hash', String, index=True)
    ts = Column('ts', DateTime, default=datetime.utcnow)

    DEFAULT_FOLDER = Path(getenv('PWD')) / 'documents'

    __table_args__ = (
        UniqueConstraint('filename', 'hash', 'userid', name='file_hash_unique'),
    )
