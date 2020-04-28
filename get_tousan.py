import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime

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
# engine = create_engine('sqlite:///:memory:')

# DBに対してORM操作するときに利用
# Sessionを通じて操作を行う
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()

# クラス
class Tousan(Base):
    
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

# 都道府県が一致する場合はprefecture_idをセットする
def address_to_prefecture_id(address):
    q=f"prefecture.str.contains('{address}')"
    res = df_prefecture.query(q)
    return int(res["id"]) if len(res["id"]) else 0

def address_to_prefecture_city_id(address):
    q = f"city.str.contains('{address}')" 
    res = df_city.query(q)
    return  list(res)


# 都道府県　変換
def prefecture(address):
    address = str(address)
    if "東京都" in address:
        res = "東京都"
    elif "県" in address[:4]:
        res = address[:address.find("県")+1]
    elif "府" in address[:4]:
        res = address[:address.find("府")+1]
    elif "道" in address[:4]:
        res = "北海道"
    else:
        res = ""
    return res

# 市町村から都道府県取得
def address_to_prefecture(address):
    address = str(address)
    res =  df_city[df_city["city"].map(lambda s: s in address)]
    res = res.iloc[0]["prefecture"] if len(res) > 0 else ""
    
    # 政令指定都市で区がないケース
    if res == "":
        res = df_city[df_city["city"].str.contains(address)]
        res = res.iloc[0]["prefecture"] if len(res) > 0 else ""
    return res


pd.set_option('display.max_rows',  500)

url = "https://www.tokyo-keizai.com/tosan-archive/page/{0}".format(1)
res = requests.get(url)
bs = BeautifulSoup(res.text)
totalpage = int(bs.select_one(".wp-pagenavi .pages").text.split(" / ")[1])

datas = []
pageindex = 1
maxpage = 5

for i in range(maxpage - pageindex):
    page = i + pageindex
    url = "https://www.tokyo-keizai.com/tosan-archive/page/{0}".format(page)
    res = requests.get(url)
    bs = BeautifulSoup(res.text)
    lists = bs.select(".page-content .archive_list")
    
    # 取得
    for l in lists:
        data = {}
        data["page"] = page
        data["date"] = l.select_one(".date").text.replace(" 公開", "")
        name_address = l.select_one("h3 a").text.split("｜")
        data["name"] = name_address[0].replace("(株)", "株式会社 ").replace("(有)", "有限会社 ")
        data["address"] = name_address[1] if len(name_address) > 1 else ""
        data["text"] = l.select_one("h4").text.replace("\t", "")
        data["url"] = l.select_one("h3 a")["href"]
        
        datas.append(data)


# 都道府県、市町村の読み込み
sql = """
SELECT id, name as prefecture
FROM prefectures a
"""
df_prefecture = pd.read_sql(sql, engine)


sql = """
SELECT b.prefecture_id, b.id as city_id, a.name as prefecture, b.name as city, a.name || b.name as prefecture_city
FROM prefectures a
INNER JOIN cities b ON a. id = b.prefecture_id
"""
df_city = pd.read_sql(sql, engine)

# pandas
df = pd.DataFrame(datas)
# 変換処理
df['date'] = pd.to_datetime(df['date'], format='%Y年%m月%d日').dt.date
df["address"] = df["address"].str.strip()
df["indastry"] = df["text"].str.extract("【業種】( .+)?【倒産")
df["type"] = df["text"].str.extract("【倒産形態】(.+?)$")
df["type"] = df["type"].str.replace("【負債総額】.+", "")
df["debt"] = df["text"].str.extract("【負債総額】(.+$)")
df["prefecture_id"] = 0
df["city_id"] = 0

# 都道府県を取得
df["prefecture"] = df["address"].map(prefecture)

# 市町村から都道府県を取得
for index, row in df.iterrows():
    if df.loc[index, "prefecture"] == "":
        df.loc[index, "prefecture"] = address_to_prefecture(row["address"])

df.to_csv("_tousan.csv")

# DB登録
df.to_sql('tmp_tousans', engine, if_exists="replace" )

sql = '''
INSERT INTO tousans (url, name, tousan_date, indastry, prefecture_id, city_id, address, note, prefecture)
SELECT url, name, date::date, indastry, prefecture_id, city_id, address, 'text', prefecture 
FROM tmp_tousans a
WHERE NOT EXISTS (
	SELECT 1 FROM tousans b
	WHERE a.url = b.url	
);
'''
t = text(sql)
try:
    session.execute(t)
    session.commit()
except :
    print("Error: INSERT tousans")


df2 = pd.read_csv("tousan.csv")
df = pd.concat([df, df2]).drop_duplicates(['url'], keep='last')
df = df[["page", "date", "name", "address", "text", "url", "indastry", "type", "debt", "prefecture_id", "city_id", "prefecture"]]
df.to_csv('tousan.csv')
df