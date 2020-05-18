import requests
import re
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd

from .db import session, engine, City, Prefecture, Tousan


# 都道府県 変換
def get_prefecture(address):
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


def get_address_to_prefecture_city(address):
    '市町村から都道府県取得'
    # 都道府県がある場合は抽出する
    prefecture = get_prefecture(address)

    # addressから都道府県以下のみ取得する
    search = "%" + str(address).replace(prefecture, '') + "%"
    city = session.query(City.id, City.prefecture_id, Prefecture.name).join(Prefecture).filter(City.name.like(search))
    if prefecture:
        city.filter(Prefecture.name == prefecture)
    res = city.first()
    
    return res


def get_tousan_list(l, page):
    'bsのリストから倒産情報を抜き出してlistで返す'
    data = {}
    data["page"] = page
    date_ = l.select_one(".date").text.replace(" 公開", "")
    data["tousan_date"] = datetime.strptime(date_, "%Y年%m月%d日").strftime("%Y-%m-%d")
    name_address = l.select_one("h3 a").text.split("｜")
    data["name"] = name_address[0].replace("(株)", "株式会社 ").replace("(有)", "有限会社 ")
    data["address"] = name_address[1] if len(name_address) > 1 else ""
    text_ = l.select_one("h4").text.replace("\t", "").strip()
    data["text"] = text_
    data["url"] = l.select_one("h3 a")["href"]

    data['indastry'] = ",".join(re.findall('【業種】(.+?)【倒産形態】', text_)).strip()
    data['type'] = re.sub('【負債総額】.+', '', ",".join(re.findall('【倒産形態】(.+?)$', text_))).strip()
    data['debt'] = ",".join(re.findall('【負債総額】(.+$)', text_)).strip()

    # 都道府県名、市町村コード、都道府県コードを取得
    data['city_id'], data['prefecture_id'], data['prefecture'] = get_address_to_prefecture_city(data['address'])

    return data


def main():
    pd.set_option('display.max_rows', 500)

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
            data = get_tousan_list(l, page)
            datas.append(data)

    # CSV保存
    df = pd.DataFrame(datas)
    df.to_csv("_tousan.csv")

    # DB登録
    for data in datas:
        # 同じURLがない場合のみ登録
        cnt = session.query(Tousan.id).filter(Tousan.url == data['url']).count()
        if cnt == 0:
            tousan = Tousan()        
            # 倒産情報の辞書をオブジェクトにセット
            for k, v in data.items():
                setattr(tousan, k, v)
            session.add(tousan)
            try:
                session.commit()
            except Exception as e:
                print("INSERT ERROR:", data)

            finally:
                print("INSERT :", data)
        

if __name__ == "__main__":
    main()
