import unittest
import time
import shutil

from sumo import csv_format

DataPath = "./tests/"

class TestCsvFormat(unittest.TestCase):
    'test class of getYahooEstate.py'

    # def setUp(self):
    #     print("setup")

    @classmethod
    def setUpClass(self):
        self.obj = csv_format.CsvFormat()

    # main
    def test_main(self):
        print('main')
        start = time.time()
        base_file = DataPath + "input/_test.csv"
        filename = DataPath + "input/test.csv"
        shutil.copy(base_file, filename)
        self.obj.main(filename)
        end = time.time() - start
        print("app_time:{0}[sec]".format(end))
        
    # 路線
    def test_estate_to_route(self):
        print('test_estate_to_route')
        str = "小田急線「町田」バス14分停歩1分"
        res = self.obj.str_routes_to_route(str)
        equal = "小田急線"
        self.assertEqual(res, equal)

    # 駅名
    def test_estate_to_station(self):
        print('test_estate_to_station')
        str = "小田急線「町田」バス14分停歩1分"
        res = self.obj.str_routes_to_station(str)
        equal = "町田"
        self.assertEqual(res, equal)

    # 交通手段バス
    def test_estate_to_traffic_bus(self):
        print('test_estate_to_traffic_bus')
        # バスあり
        str = "小田急線「町田」バス14分停歩1分"
        res = self.obj.str_routes_to_traffic_bus(str)
        equal = '14'
        self.assertEqual(res, equal)

        str = "京王高尾線「めじろ台」バス9分停歩2分"
        res = self.obj.str_routes_to_traffic_bus(str)
        equal = '9'
        self.assertEqual(res, equal)

        # バスなし
        str = "ＪＲ中央線「武蔵小金井」徒歩5分"
        res = self.obj.str_routes_to_traffic_bus(str)
        equal = ''
        self.assertEqual(res, equal)

    # 交通手段
    def test_estate_to_traffic_work(self):
        print('test_estate_to_traffic_work')
        # 徒歩パターン
        str = "小田急線「町田」徒歩4分"
        res = self.obj.str_routes_to_traffic_work(str)
        equal = '4'
        self.assertEqual(res, equal)

        # 停歩パターン
        str = "小田急線「町田」バス14分停歩1分"
        res = self.obj.str_routes_to_traffic_work(str)
        equal = '1'
        self.assertEqual(res, equal)

        # 歩
        str = "ＪＲ函館本線「ニセコ」歩97分"
        res = self.obj.str_routes_to_traffic_work(str)
        equal = '97'
        self.assertEqual(res, equal)

        # 車 Km
        str = "ＪＲ吾妻線「万座・鹿沢口」車6.4km"
        res = self.obj.str_routes_to_traffic_work(str)
        equal = ''
        self.assertEqual(res, equal)

    def test_str_routes_to_traffic_car(self):
        print('test_str_routes_to_traffic_car')
        # 車 Km
        str = "ＪＲ吾妻線「万座・鹿沢口」車6.4km"
        res = self.obj.str_routes_to_traffic_car(str)
        equal = '6.4'
        self.assertEqual(res, equal)

        # 車なし
        str = "小田急線「町田」バス14分停歩1分"
        res = self.obj.str_routes_to_traffic_car(str)
        equal = ''
        self.assertEqual(res, equal)

    # 販売価格の文字列を数字に変更
    def test_str_price_to_number(self):
        print('test_str_price_to_number')
        # 億があるパターン
        str = "1億2100万円"
        res = self.obj.str_price_to_number(str)
        equal = 12100
        self.assertEqual(res, equal)

        # 億がないパターン
        str = "2100万円"
        res = self.obj.str_price_to_number(str)
        equal = 2100
        self.assertEqual(res, equal)

        # ３億円
        str = "3億円"
        res = self.obj.str_price_to_number(str)
        equal = 30000
        self.assertEqual(res, equal)

        # 21133万2000円
        str = "21133万2000円"
        res = self.obj.str_price_to_number(str)
        equal = 21133
        self.assertEqual(res, equal)

        # 文字列あり
        str = "5190万円※権利金含む5190万円"
        res = self.obj.str_price_to_number(str)
        equal = 5190
        self.assertEqual(res, equal)

        # 文字列あり 億含む
        str = "2億5190万円※権利金含む5190万円"
        res = self.obj.str_price_to_number(str)
        equal = 25190
        self.assertEqual(res, equal)

        # ～を含む
        str = "4800万円～6280万円"
        res = self.obj.str_price_to_number(str)
        equal = 4800
        self.assertEqual(res, equal)

        # ～を含む 億あり
        str = "2億4800万円～6280万円"
        res = self.obj.str_price_to_number(str)
        equal = 24800
        self.assertEqual(res, equal)

        # ～を含む 万円なし
        str = "4800～6280万円"
        res = self.obj.str_price_to_number(str)
        equal = 4800
        self.assertEqual(res, equal)

        # 最初に文字あり
        str = "お買い得！8800～9280万円"
        res = self.obj.str_price_to_number(str)
        equal = 8800
        self.assertEqual(res, equal)



if __name__ == "__main__":
    unittest.main()
