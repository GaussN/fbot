from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Link(Base):
    __tablename__ = 'links'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    urn = Column('uri', String, unique=True, index=True, nullable=False)
    user_tg_id = Column('user_tg_id', String, nullable=False)
    file_id = Column('file_id', ForeignKey('files.id'))
    live_until = Column('live_until', DateTime, nullable=True, default=None)
    number_uses = Column('number_uses', Integer, nullable=True, default=None)
    ts = Column('ts', DateTime, default=datetime.utcnow)
    file = relationship('File', backref='links', cascade='all,delete')

    def check(self) -> bool:
        return all((
            self.live_until > datetime.utcnow() if self.live_until else True,
            self.number_uses > 0 if self.number_uses is not None else True
        ))
