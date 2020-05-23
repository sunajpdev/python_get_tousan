from sqlalchemy import Column, Integer, String, DateTime, Sequence
from settings.db import engine, Base
from sqlalchemy.sql import func
from datetime import datetime
import sys

# クラス
class Route(Base):
    '路線'
    __tablename__ = 'routes'
    id = Column(Integer, primary_key=True,  autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return "<{self.name}: {self.id}>"


Base.metadata.create_all(engine)