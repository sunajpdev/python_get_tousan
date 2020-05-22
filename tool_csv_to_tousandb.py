import sys

from src import get_tousan

if __name__ == "__main__":
    argv = sys.argv

    if len(argv) == 2:
        # 引数がある場合はCSVからのデータ取り込みをする
        get_tousan.save_csv_file_to_db(argv[1])

    else:
        print("引数に読み込みするファイル名を指定！")
    