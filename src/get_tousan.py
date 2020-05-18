import requests
import re
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd

from .db import session, engine, City, Prefecture, Tousan
from .lib.lib_csv import LibCsv
from .lib.address import *

TMP_CSV_FILENAME = "./tmp/_tousan.csv"


def get_tousan_list(l, page):
    'bsのリストから倒産情報を抜き出してlistで返す'
    data = {}
    data["page"] = page
    date_ = l.select_one(".date").text.replace(" 公開", "")
    data["tousan_date"] = datetime.strptime(date_, "%Y年%m月%d日").strftime("%Y-%m-%d")
    name_address = l.select_one("h3 a").text.split("｜")
    data["name"] = name_address[0].replace("(株)", "株式会社 ").replace("(有)", "有限会社 ").strip()
    data["address"] = name_address[1].strip() if len(name_address) > 1 else ""
    text_ = l.select_one("h4").text.replace("\t", "").strip()
    data["text"] = text_
    data["url"] = l.select_one("h3 a")["href"].strip()

    data['indastry'] = ",".join(re.findall('【業種】(.+?)【倒産形態】', text_)).strip()
    data['type'] = re.sub('【負債総額】.+', '', ",".join(re.findall('【倒産形態】(.+?)$', text_))).strip()
    data['debt'] = ",".join(re.findall('【負債総額】(.+$)', text_)).strip()

    # 都道府県名、市町村コード、都道府県コードを取得
    data['city_id'], data['prefecture_id'], data['prefecture'] = get_address_to_prefecture_city(data['address'])

    return data


def get_data_to_list():
    'WebPegaを取得し、倒産情報をリストで返す'
    pd.set_option('display.max_rows', 500)

    url = "https://www.tokyo-keizai.com/tosan-archive/page/{0}".format(1)
    res = requests.get(url)
    bs = BeautifulSoup(res.text, 'lxml')
    totalpage = int(bs.select_one(".wp-pagenavi .pages").text.split(" / ")[1])

    datas = []
    pageindex = 1
    maxpage = 5

    for i in range(maxpage - pageindex):
        page = i + pageindex
        url = "https://www.tokyo-keizai.com/tosan-archive/page/{0}".format(page)
        res = requests.get(url)
        bs = BeautifulSoup(res.text, 'lxml')
        lists = bs.select(".page-content .archive_list")
        
        # 取得
        for l in lists:
            data = get_tousan_list(l, page)
            datas.append(data)
    return datas


def save_db(datas):
    'リストの内容をDBに登録する'
    for data in datas:
        # 同じURLがない場合のみ登録
        cnt = session.query(Tousan.id).filter(Tousan.url == data['url']).count()
        if cnt == 0:
            try:
                engine.execute(Tousan.__table__.insert(), data)
            except:
                print("INSERT ERROR: ", data)
            finally:
                print("INSERT :", data)
        else:
            print("SKIP :", data["name"], cnt)


def main():
    # 倒産情報を取得して、CSVに保存
    datas = get_data_to_list()

    # CSVに保存
    fname = TMP_CSV_FILENAME
    lib_csv = LibCsv()
    lib_csv.save_csv_dict(fname, datas)

    # CSVを読み込み
    datas = lib_csv.open_csv_dict(fname)
    # DBに保存
    save_db(datas)


if __name__ == "__main__":
    main()
