import requests
import os
import shutil
import zipfile

import pandas as pd
import mojimoji

from sqlalchemy.sql import text

from src.db import session, engine


TMP_DIR = "./tmp/"
DOWNLOAD_FILENAME = TMP_DIR + "ken_all.zip"
CSV_FILENAME = TMP_DIR + "KEN_ALL.CSV"

def download(url, filename):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        with open(filename, 'wb') as file:
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, file)
    return filename


def read_csv_df(filename):
    "CSVから不要項目を除外して読み込む"
    # 不要項目の変換処理    
    names = ['citycode', 'post_old', 'post', 'prefecture_kana', 'city_kana', 'address_kana', 'prefecture', 'city', 'address', "1", "2", "3", "4", "5", "6"]
    df = pd.read_csv(filename, encoding="SHIFT-JIS", dtype=str, names=names, header=None)

    # kanaを半角から全角に変換
    df["prefecture_kana"] = df["prefecture_kana"].map(mojimoji.han_to_zen)
    df["city_kana"] = df["city_kana"].map(mojimoji.han_to_zen)
    df["address_kana"] = df["address_kana"].map(mojimoji.han_to_zen)

    # 不要な行を除外
    df = df[df['address'] != "以下に掲載がない場合"]

    # 不要な列を除外
    df = df[["post","citycode", "prefecture", "city", "address", "prefecture_kana", "city_kana", "address_kana"]].sort_values('post')

    return df


def run_sql(sql, error_message=""):
    t = text(sql)
    try:
        session.execute(t)
        session.commit()
    except :
        print("Error:" + error_message)


def insert_db():
    "tmp_postに登録された情報を各テーブルに保存する"

    # 都道府県追加
    sql = """
    INSERT INTO prefectures (name, kana)
    SELECT a.prefecture , a.prefecture_kana
    FROM tmp_posts a
    GROUP BY prefecture , prefecture_kana 
    ORDER BY min( citycode)
    ;
    """
    run_sql(sql, "INSERT prefectures")


    # 市町村追加
    sql = """
    INSERT INTO cities (prefecture_id , citycode , name, kana)
    SELECT b.id AS prefecture_id , a.citycode , a.city , a.city_kana
    FROM tmp_posts a
    INNER JOIN prefectures b ON b.name = a.prefecture 
    GROUP BY a.citycode, a.city , a.city_kana , b.id
    ORDER BY min( citycode);
    """

    run_sql(sql, "INSERT cities")


    # 郵便番号追加
    sql = """
    INSERT INTO posts (post, prefecture_id , city_id, address, address_kana )
    SELECT tp.post, p.id AS prefecture_id, c.id AS city_id, tp.address , tp.address_kana 
    FROM tmp_posts tp 
    INNER JOIN prefectures p ON p.name = tp.prefecture 
    INNER JOIN cities c ON c.name = tp.city AND p.id = c.prefecture_id
    WHERE NOT EXISTS (
        SELECT 1
        FROM posts a
        WHERE a.post = tp.post AND a.address = tp.address AND a.address_kana = tp.address_kana 
    )
    ORDER BY p.id, c.id, tp.post;
    """

    run_sql(sql, "INSERT posts")


def main():

    # ダウンロードファイルがある場合は処理をスキップ
    if not os.path.isfile(DOWNLOAD_FILENAME):
        # ダウンロード
        url = "https://www.post.japanpost.jp/zipcode/dl/oogaki/zip/ken_all.zip"
        download(url, DOWNLOAD_FILENAME)

        # ファイルを解凍
        with zipfile.ZipFile(DOWNLOAD_FILENAME) as zip:
            zip.extractall(TMP_DIR)
    
    # CSVファイルをtmp_tableに保存後、都道府県、市町村、郵便番号テーブルに保存
    df = read_csv_df(CSV_FILENAME)
    df.to_sql('tmp_posts', engine, if_exists="replace" )
    insert_db()


if __name__ == "__main__":
    main()