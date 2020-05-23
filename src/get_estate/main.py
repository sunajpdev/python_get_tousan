import os
import sys
import datetime
from concurrent.futures import ThreadPoolExecutor

from sumo import estate_sumo, csv_union
from sumo.csv_format import CsvFormat


SiteUrls = [
    {
        "name": "千葉県",
        "url": "https://suumo.jp/jj/bukken/ichiran/JJ012FC002/?ar=030&bknlistmodeflg=2&bs=011&cn=9999999&cnb=0&ekTjCd=&ekTjNm=&kb=1&kt=9999999&mb=0&mt=9999999&ta=12&tj=0&po=0&pj=1&pc=100"
    },
    {
        "name": "東京", 
        "url": "https://suumo.jp/jj/bukken/ichiran/JJ012FC002/?ar=030&bknlistmodeflg=2&bs=011&cn=9999999&cnb=0&ekTjCd=&ekTjNm=&kb=1&kt=9999999&mb=0&mt=9999999&ta=13&tj=0&po=0&pj=1&pc=100"
    },
    {
        "name": "神奈川県",
        "url": "https://suumo.jp/jj/bukken/ichiran/JJ012FC002/?ar=030&bknlistmodeflg=2&bs=011&cn=9999999&cnb=0&ekTjCd=&ekTjNm=&kb=1&kt=9999999&mb=0&mt=9999999&ta=14&tj=0&po=0&pj=1&pc=100"
    },
    {
        "name": "埼玉県",
        "url": "https://suumo.jp/jj/bukken/ichiran/JJ012FC002/?ar=030&bknlistmodeflg=2&bs=011&cn=9999999&cnb=0&ekTjCd=&ekTjNm=&kb=1&kt=9999999&mb=0&mt=9999999&ta=11&tj=0&po=0&pj=1&pc=100"
    },
]

MaxWorkers = 10
DataPath = ""
GetFilePath = "./data/get"
ProcessingFilePath = "./data/processing"
ProcessingTargetFile = "./data/get/*.*"

def thread(title, base_url, save_path, save_file_type):
    'ベースページを取得して総ページを取得. 処理はthreadsに格納して並行処理をする'
    # 1.URLよりHTMLを取得
    obj = estate_sumo.EstateSumo()
    print("<<First Data Get>>")
    get_html = obj.get_html_from_url(base_url)
    bs = obj.html_to_bs(get_html)
    # 2.総件数、総ページ数を取得、
    # total_estate = obj.get_total(bs)
    total_page = obj.get_total_page(bs)
    print("total_page: ", total_page)

    # スレッド
    tpe = ThreadPoolExecutor(max_workers=MaxWorkers)

    print(title, total_page)
    for i in range(int(total_page)):
        # iは0から始まり、pageは1から始まるので調整
        cnt = i + 1
        # tasks.get_estate(title, base_url, save_path, cnt, save_file_type)
        print("<<tpe.submit>>", title, cnt)
        tpe.submit(obj.main_get_url_to_html_savefile, title, base_url, save_path, cnt, save_file_type)

    # 全スレッドが終了するまで待機
    tpe.shutdown()


def csv_merge(get_path, save_path):
    '取得したCSVを１つのファイルにまとめる'

    print("<<CSV Save Start>>")
    filename = csv_union.main(get_path, save_path)
    print("<<CSV Save End>>")
    return filename


def csv_convert(filename):
    '駅名などの項目を抽出する'

    # 集約処理が成功した場合のみ実行
    if filename is not False:
        print("<<CSV Format Start>>")
        cf = CsvFormat()
        cf.main(filename)
        print("<<CSV Format End>>")
    else:
        print("# CSV Save: message NoFiles")


def main():
    # すでに同一日の取込済みcsvがある場合は処理をしない
    today = datetime.date.today()
    filename = ProcessingFilePath + "/" + str(today) + ".csv"
    if os.path.isfile(filename):
        print("<<Skip File Existence>>", filename)
        exit()

    # 取得処理
    for site in SiteUrls:
        title = site["name"]
        base_url = site["url"]
        save_file_type = "csv"

        print("<<Sumo Get Start>>", title)
        thread(title, base_url, GetFilePath, save_file_type)
        print("<<Sumo Get Start>>", title)

    # Merge処理
    filename = csv_merge(ProcessingTargetFile, ProcessingFilePath)

    # コンバート処理
    csv_convert(filename)
    

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1] == 'merge':
        csv_merge(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'cnv':
        # 引数が cnv ならコンバート処理のみ行う
        csv_convert(sys.argv[2])
