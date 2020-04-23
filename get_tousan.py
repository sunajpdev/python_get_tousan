import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

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
        print(data)

# pandas
df = pd.DataFrame(datas)
df['date'] = pd.to_datetime(df['date'], format='%Y年%m月%d日').dt.date
df.to_csv("_tousan.csv")

df2 = pd.read_csv("tousan.csv")
df3 = pd.concat([df, df2]).drop_duplicates(['url'], keep='last')
df4 = df3[["page", "date", "name", "address", "text", "url"]]
df4.to_csv('tousan.csv')