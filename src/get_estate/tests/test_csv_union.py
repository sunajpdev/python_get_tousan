import unittest
import os
import shutil

from sumo import csv_union as ce


DataPath = "./tests/"

class TestEstateSumo(unittest.TestCase):
    'test class of '

    @classmethod
    def setUpClass(self):
        'テスト開始時に一度だけする処理'
        pass

    def setUp(self):
        '各テスト毎に実行する処理'
        pass

    def test_main(self):
        'ファイルが正常に作成されるかチェック'
        save_path = DataPath + "output"
        get_path = DataPath + "input/test*.csv"
        
        # 作業ファイルを作成
        base_file = DataPath + "input/_test.csv"
        get_path1 = DataPath + "input/test1.csv"
        shutil.copy(base_file, get_path1)

        filename = ce.main(get_path, save_path)
        # ファイルが存在するかチェック
        res = os.path.isfile(filename)
        self.assertTrue(res)

        # ファイルの列数をカウント
        rows = []
        with open(filename, encoding='utf-8_sig') as f:
            for row in f:
                rows.append(row)
        res = len(rows)
        equal = 201 # 100行＋100行 + タイトル1行
        self.assertEqual(res, equal)
        
        # 出力ファイルを削除
        os.remove(filename)
        

if __name__ == "__main__":
    unittest.main()
