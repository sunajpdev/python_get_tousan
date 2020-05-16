import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv

load_dotenv('.env')

db = os.environ.get("DB")
driver = os.environ.get("DRIVER")
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")
port = os.environ.get("PORT")
database = os.environ.get("DATABASE")

db_url = f"{db}+{driver}://{username}:{password}@{host}:{port}/{database}"

print("db_url: ",db_url)

# DB接続するためのEngineインスタンス
engine = create_engine(db_url, echo=True)
# engine = create_engine('sqlite:///:memory:')

# DBに対してORM操作するときに利用
# Sessionを通じて操作を行う
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()

# クラス
class Prefecture(Base):
    "都道府県"
    __tablename__ = 'prefectures'

    id = Column(Integer, primary_key=True,  autoincrement=True, nullable=False)    
    name = Column(String(10), nullable=False, index=True, unique=True)
    kana = Column(String(10), nullable=False, index=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # リレーション
    #cities = relationship("City", backref="prefectures")
    #posts = relationship("Post", backref="prefectures")
    
    def __repr__(self):
        return "id:{}".format(id)

    
class City(Base):
    "市町村"
    __tablename__ = 'cities'
    __table_args__ = (UniqueConstraint('prefecture_id', 'name'),{})

    id = Column(Integer, primary_key=True,  autoincrement=True, nullable=False) 
    prefecture_id = Column(Integer, ForeignKey('prefectures.id'))
    citycode = Column(String(10), nullable=False, index=True)
    name = Column(String(20), nullable=False, index=True)
    kana = Column(String(30), nullable=False, index=True)

    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(DateTime(timezone=True), server_default=func.now())

    #posts = relationship("Post", backref="cities")
    
    def __repr__(self):
        return "id:{}".format(id)



class Post(Base):
    "郵便番号"
    __tablename__ = 'posts'
    # 複数条件でユニーク 大阪の八尾木がカナだけ違うためaddress_kanaも追加
    __table_args__ = (UniqueConstraint('post','prefecture_id', 'city_id', 'address', 'address_kana'),{})

    id = Column(Integer, primary_key=True,  autoincrement=True, nullable=False)    
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
    prefecture= Column(String(10), index=True)
    indastry = Column(String(50))
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
