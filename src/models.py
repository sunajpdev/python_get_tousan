from sqlalchemy import Column, Integer, String, Text, DATE, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from .db import engine, Base


# クラス
class City(Base):
    "市町村"
    __tablename__ = 'cities'
    __table_args__ = (UniqueConstraint('prefecture_id', 'name'),{})

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False) 
    prefecture_id = Column(Integer, ForeignKey('prefectures.id'))
    citycode = Column(String(10), nullable=False, index=True)
    name = Column(String(20), nullable=False, index=True)
    kana = Column(String(30), nullable=False, index=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())

    prefecture = relationship("Prefecture", back_populates = "cities")
    
    def __repr__(self):
        return "id:{}".format(id)


class Prefecture(Base):
    "都道府県"
    __tablename__ = 'prefectures'

    id = Column(Integer, primary_key=True,  autoincrement=True, nullable=False)    
    name = Column(String(10), nullable=False, index=True, unique=True)
    kana = Column(String(10), nullable=False, index=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())
    
    cities = relationship("City", order_by = City.id, back_populates="prefecture")

    def __repr__(self):
        return "id:{}".format(id)


class Post(Base):
    "郵便番号"
    __tablename__ = 'posts'
    # 複数条件でユニーク 大阪の八尾木がカナだけ違うためaddress_kanaも追加
    __table_args__ = (UniqueConstraint('post', 'prefecture_id', 'city_id', 'address', 'address_kana'),{})

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)    
    post = Column(String(10), nullable=False, index=True)
    prefecture_id = Column(Integer, ForeignKey('prefectures.id') )
    city_id = Column(Integer, ForeignKey('cities.id'))
    address = Column(String(50), nullable=False, index=True)
    address_kana = Column(String(80), nullable=False, index=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())
        
    def __repr__(self):
        return "id:{}".format(id)


class Tousan(Base):
    "倒産情報"
    __tablename__ = 'tousans'
    id = Column(Integer, primary_key=True,  autoincrement=True, nullable=False)
    tousan_date = Column(DATE)
    name = Column(String(255), nullable=False, index=True)
    prefecture = Column(String(10), index=True)
    indastry = Column(String(50))
    type = Column(String(50))
    debt = Column(String(100))
    prefecture_id = Column(Integer, index=True)
    city_id = Column(Integer, index=True)
    address = Column(String(255))
    note = Column(Text)
    url = Column(String(255), nullable=False, unique=True)
    
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return "<Tousan(id='%s', name='%s', date='%s')" % (self.id, self.name, self.date)


Base.metadata.create_all(engine)
