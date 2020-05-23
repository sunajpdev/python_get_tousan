import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
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


# DB接続するためのEngineインスタンス
# engine = create_engine(db_url, echo=True)
engine = create_engine(db_url, echo=False)
# engine = create_engine('sqlite:///:memory:')

# DBに対してORM操作するときに利用
# Sessionを通じて操作を行う
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()
