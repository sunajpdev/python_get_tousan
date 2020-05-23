# setting.py
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

dialect = "postgresql"
driver = "psycopg2"
username = "postgres"
password = ""
host = "localhost"
port = "5432"
database = "postgres"
charset_type = "utf8"
db_url = f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"

# DB接続するためのEngineインスタンス
engine = create_engine(db_url, echo=True)

# DBに対してORM操作するときに利用
# Sessionを通じて操作を行う
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()

