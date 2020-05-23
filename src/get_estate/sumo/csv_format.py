import sys
import re
import glob

from bs4 import BeautifulSoup
import pandas as pd

header = (
    'name', 'url', 'address_str', 'floor_size', 'balcony_size', 'floorplan_str', 'construction_date', 'price_str', 'routes_str', 'comment', 'comment_staff',
    'route', 'station', 'bus_time', 'work_time', 'car_distrance', 'price', 'prefecture', 'city', 'address', 'floorplan'
)

rows = []
class CsvFormat():
    def main(self, filename):

        # csv読み込み pandasは遅いので辞書型に変換して処理
        df = pd.read_csv(filename)
        list_ = df.values.tolist()
        keys = df.columns
        csv_rows = []
        # 辞書に変換
        for values in list_:
            csv_rows.append({key: val for key, val in zip(keys, values)})

        # フォーマット処理
        for row in csv_rows:
            row["route"] = self.str_routes_to_route(row["routes_str"])
            row["station"] = self.str_routes_to_station(row["routes_str"])
            row["bus_time"] = self.str_routes_to_traffic_bus(row["routes_str"])
            row["work_time"] = self.str_routes_to_traffic_work(row["routes_str"])
            row["car_distance"] = self.str_routes_to_traffic_car(row["routes_str"])
            row["price"] = self.str_price_to_number(row["price_str"])
            rows.append(row)
            # df["prefecture"][i] = self.address_str_to_prefecture(df["address"][i])
        
        df = pd.DataFrame(rows)
        df.to_csv(filename)
        
    # 都道府県を抽出
    def address_str_to_prefecture(self, address_str):
        return address_str

    # 路線を取得
    def str_routes_to_route(self, str_routes):
        res = str_routes.split('「')[0]
        return res

    # 駅を取得
    def str_routes_to_station(self, str_routes):
        res = str_routes.split('「')[1].split('」')[0]
        return res

    # 交通手段がバスの場合その時間、ない場合は空の文字列を返す
    def str_routes_to_traffic_bus(self, str_routes):
        pattern = '.*?バス(.+?)分'
        result = re.compile(pattern).match(str_routes)
        res = result[1] if result else ''
        return res

    # 交通手段 徒歩時間、ない場合は空の文字列を返す
    def str_routes_to_traffic_work(self, str_routes):
        pattern = '.*?(徒歩|停歩|歩)(.+?)分'
        result = re.compile(pattern).match(str_routes)
        res = result[2] if result else ''
        return res

    # 交通手段 車のkm,ない場合は空の文字列を返す
    def str_routes_to_traffic_car(self, str_routes):
        pattern = '.*?車(.+)km'
        result = re.compile(pattern).match(str_routes)
        res = result[1] if result else ''
        return res

    # 販売価格の文字列を数字で返す
    def str_price_to_number(self, str_price):
        # res = str_price.replace('億円', '0000').replace('万円', '').replace('億', '')
        if '億円' in str_price:
            en = str_price.split('億円')
            res = en[0] + "0000"
        elif '億' in str_price:
            en = str_price.split('万円')
            res = en[0].replace('億', '') if len(en) > 1 else 0
        elif '万円' in str_price:
            en = str_price.split('万円')
            res = en[0] if len(en) > 1 else 0
        elif '万' in str_price:
            en = str_price.split('万')
            res = en[0] if len(en) > 1 else 0
        else:
            res = "0"
        # 〜が含まれている場合
        if '～' in str(res):
            en = res.split('～')
            res = en[0] if len(en) > 1 else 0
        # 先頭に文字列が含まれているケース
        res = re.sub(r'\D', '', str(res))

        res = int(res) if res.isnumeric() else 0
        return res

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(sys.argv)
        files = glob.glob(sys.argv[1]+'*.csv')
        if len(files) > 0:
            cf = CsvFormat()
            print(files)
            for filename in files:
                print(f"<START : {filename}>")
                cf.main(filename) 
    else:
        print("引数にパスを指定して")