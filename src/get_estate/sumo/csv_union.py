import os
import shutil
import pandas as pd
import glob
import pathlib

from datetime import datetime

ErrorPath = './data/error'

def main(get_path, save_path):
    # ファイル名に日付名をつける
    ymd = datetime.today().strftime('%Y-%m-%d')
    save_filename = "{0}/{1}.csv".format(save_path, ymd)

    # ファイルを抽出して保存
    all_files = glob.glob(get_path)
    all_files.sort()

    # ファイルがない場合は処理を終了
    if len(all_files) == 0:
        return False

    # 指定ファイル(CSV)をひとつのCSVにして保存
    list_pd = []
    for file_ in all_files:
        print("union filename: ", file_)
        suffix = pathlib.Path(file_).suffix
        # 拡張子がCSVまたはjsonで処理を分ける それ以外はスキップ
        if suffix == '.csv':
            try:
                df = pd.read_csv(file_)
                list_pd.append(df)
            except:
                print("FileError:", file_)
                shutil.move(file_, ErrorPath)


    # 'pandasの複数のlistを結合'
    df = pd.concat(list_pd, join='outer')

    df.to_csv(save_filename, encoding="utf-8_sig", index=False)

    # 取得ファイルを削除する
    for filename in all_files:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    return save_filename


if __name__ == "__main__":
    save_path = "./processing"
    get_path = "./data/get/*.*"

    save_filename = main(get_path, save_path)
