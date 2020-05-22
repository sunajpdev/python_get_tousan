import sys
import requests
import re
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from .db import session, engine, City, Prefecture, Tousan
from .lib.lib_csv import LibCsv
from .lib.address import get_address_to_prefecture_city

TMP_CSV_FILENAME = "./tmp/_tousan.csv"


def get_tousan_list(l, page):
    'bsのリストから倒産情報を抜き出してlistで返す'
    data = {}
    date_ = l.select_one(".date").text.replace(" 公開", "")
    data["tousan_date"] = datetime.strptime(date_, "%Y年%m月%d日").strftime("%Y-%m-%d")
    name_address = l.select_one("h3 a").text.split("｜")
    data["name"] = name_address[0].replace("(株)", "株式会社 ").replace("(有)", "有限会社 ").strip()
    data["address"] = name_address[1].strip() if len(name_address) > 1 else ""
    note = l.select_one("h4").text.replace("\t", "").strip()
    data["note"] = note
    data["url"] = l.select_one("h3 a")["href"].strip()

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
    'リストの内容をDBに登録。コミット数した件数を返す'
    commit_count = 0
    for data in datas:
        # 空の要素を削除
        data = {k:v for k,v in data.items() if v != ''}
        # ユニークキー違反 url エラーをスキップ
        sql = insert(Tousan).on_conflict_do_nothing(
            index_elements=["url"]
        )
        try:
            session.execute(sql, data)
            commit_count += 1
        except:
            print("SKIP: ", data["name"])
    session.commit()
    return commit_count


def save_csv_file_to_db(fname):
    'CSVファイル名を指定してDBに保存'
    # CSVを読み込み
    lib_csv = LibCsv()
    datas = lib_csv.open_csv_dict(fname)

    # 都道府県が入っていない場合に備えた処理
    datas_prefecture = []
    for data in datas:
        data['city_id'], data['prefecture_id'], data['prefecture'] = get_address_to_prefecture_city(data['address'])
        
        note = data["note"]
        if note:
            data['indastry'] = ",".join(re.findall('【業種】(.+?)【倒産形態】', note)).strip()
            data['type'] = re.sub('【負債総額】.+', '', ",".join(re.findall('【倒産形態】(.+?)$', note))).strip()
            data['debt'] = ",".join(re.findall('【負債総額】(.+$)', note)).strip()

        datas_prefecture.append(data)


    # DBに保存
    commit_count = save_db(datas_prefecture)
    return commit_count

def main():
    '倒産情報を取得して、CSVに保存'
    datas = get_data_to_list()

    # CSVに保存
    fname = TMP_CSV_FILENAME
    lib_csv = LibCsv()
    lib_csv.save_csv_dict(fname, datas)

    # DB保存
    commit_count = save_csv_file_to_db(fname)
    print("SAVE DB commit count:", commit_count)
