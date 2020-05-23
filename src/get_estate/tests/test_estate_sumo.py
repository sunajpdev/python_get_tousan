import unittest
import os
from sumo import estate_sumo

# データチェック用サイトリスト
SiteUrls = [
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
    {
        "name": "千葉県",
        "url": "https://suumo.jp/jj/bukken/ichiran/JJ012FC002/?ar=030&bknlistmodeflg=2&bs=011&cn=9999999&cnb=0&ekTjCd=&ekTjNm=&kb=1&kt=9999999&mb=0&mt=9999999&ta=12&tj=0&po=0&pj=1&pc=100"
    },
]


DataPath = "./tests/"

class TestEstateSumo(unittest.TestCase):
    'test class of getYahooEstate.py'

    # def setUp(self):
    #     print("setup")

    # 取得するHTMLのサンプル 
    @classmethod
    def estate_html(self):
        path =  DataPath + "input/sample_test_sumo_html_20200403_simple.txt"
        with open(path) as f:
            html = f.read()
        return html

    @classmethod
    def setUpClass(self):
        self.obj = estate_sumo.EstateSumo()
        self.html = self.estate_html()
        self.bs = self.obj.html_to_bs(self.html)
        self.estates = self.obj.html_to_estates(self.bs)

    def test_html_to_bs(self):
        'サンプルHTMLで確認 beatifulsoupオブジェクトを返す'
        print('test_html_to_bs(self):')
        html = "<html><div class='pagination_set-hit'>9999件</div></html>"
        bs = self.obj.html_to_bs(html)
        equal_html = "9999件"
        self.assertEqual(equal_html, bs.get_text())

    def test_get_total(self):
        '総件数を取得 URLはテスト setUpClassに記載'
        print('test_get_total(self):')
        # 数値が取れる
        html = "<html><div class='pagination_set-hit'>9999件</div></html>"
        bs = self.obj.html_to_bs(html)
        total = self.obj.get_total(bs)
        equal_total = 9999
        self.assertEqual(equal_total, total)

        # エラーにならず0が返る
        html = "<html><div class='pagination_set-hit'>ほげ</div></html>"
        bs = self.obj.html_to_bs(html)
        total = self.obj.get_total(bs)
        equal_total = 0
        self.assertEqual(equal_total, total)

        # エラーにならず0が返る
        html = "<html></html>"
        bs = self.obj.html_to_bs(html)
        total = self.obj.get_total(bs)
        equal_total = 0
        self.assertEqual(equal_total, total)

    def test_get_total_page(self):
        '総ページ数を取得 サンプルhtml'
        print('test_get_total_page')
        html = """
            <html>
                <ol class='pagination-parts'>
                    <li>1</li>
                    <li>2</li>
                    <li>3</li>
                    <li class='pagination-current'>4</li>
                </ol>
            </html>
        """
        bs = self.obj.html_to_bs(html)
        total = self.obj.get_total_page(bs)
        equal_total = 4
        self.assertEqual(equal_total, total)

        # タグがない状態でも0が返る
        html = "<html></html>"
        bs = self.obj.html_to_bs(html)
        total = self.obj.get_total_page(bs)
        equal_total = 0
        self.assertEqual(equal_total, total)

        # 空文字列でも0が返る
        html = ""
        bs = self.obj.html_to_bs(html)
        total = self.obj.get_total_page(bs)
        equal_total = 0
        self.assertEqual(equal_total, total)

    # 建物のBSを取得 件数でチェック
    def test_html_to_estates(self):
        print('test_html_to_estates')
        estates = self.obj.html_to_estates(self.bs)
        estates_count = len(estates)
        equal_estates_count = 100
        self.assertEqual(estates_count, equal_estates_count)

    # 建物名
    def test_estate_to_name(self):
        print('test_estate_to_name')
        res = self.obj.estate_to_name(self.estates[0])
        equal = "藤の台団地"
        self.assertEqual(res, equal)

    # URL
    def test_estate_to_url(self):
        print('test_estate_to_url')
        res = self.obj.estate_to_url(self.estates[0])
        equal = "https://suumo.jp/chukomansion/__JJ_JJ010FJ100_arz1030z2bsz1011z2ncz192292782.html"
        self.assertEqual(res, equal)

    # 所在地
    def test_estate_to_address(self):
        print('test_estate_to_address')
        estate_address = self.obj.estate_to_address(self.estates[0])
        equal_estate_address = "東京都町田市本町田"
        self.assertEqual(estate_address, equal_estate_address)

        estate_address = self.obj.estate_to_address(self.estates[11], 1)
        equal_estate_address = "東京都杉並区久我山１"
        self.assertEqual(estate_address, equal_estate_address)

    # 路線や交通手段の文字列取得
    def test_estate_to_str_routes(self):
        print('test_estate_to_str_routes')
        res = self.obj.estate_to_str_routes(self.estates[0])
        equal = "小田急線「町田」バス14分停歩4分"
        self.assertEqual(res, equal)

    # 販売価格
    def test_estate_to_price(self):
        print('test_estate_to_price')
        res = self.obj.estate_to_price(self.estates[0])
        equal = '980万円'
        self.assertEqual(res, equal)

    # 専有面積不要な文字列クリア
    def test_clean_str_floor_size(self):
        print('test_clean_str_floor_size')
        str = "56.54m2（壁芯）"
        res = self.obj.clean_str_floor_size(str)
        equal = '56.54'
        self.assertEqual(res, equal)

        # 前に余計な文字列があるケース
        str = "テスト56.54m2（壁芯）"
        res = self.obj.clean_str_floor_size(str)
        equal = '56.54'
        self.assertEqual(res, equal)

        # 平米がないケース
        str = "テスト56.54（壁芯）"
        res = self.obj.clean_str_floor_size(str)
        equal = ''
        self.assertEqual(res, equal)

        # バルコニー 文字列がないケース
        str = ""
        res = self.obj.clean_str_floor_size(str)
        equal = ''
        self.assertEqual(res, equal)

        str = "-"
        res = self.obj.clean_str_floor_size(str)
        equal = ''
        self.assertEqual(res, equal)

    # 専有面積
    def test_estate_to_floor_size(self):
        print('test_estate_to_floor_size')
        res = self.obj.estate_to_floor_size(self.estates[0])
        equal = "48.85"
        self.assertEqual(res, equal)

    # バルコニー面積
    def test_estate_to_balcony_size(self):
        print('test_estate_to_balcony_size')
        res = self.obj.estate_to_balcony_size(self.estates[0])
        equal = "6"
        self.assertEqual(res, equal)

        res = self.obj.estate_to_balcony_size(self.estates[6])
        equal = ""
        self.assertEqual(res, equal)

    # 部屋間取り
    def test_estate_to_floorplan(self):
        print('test_estate_to_floorplan')
        res = self.obj.estate_to_floorplan(self.estates[0])
        equal = "2LDK"
        self.assertEqual(res, equal)

        res = self.obj.estate_to_floorplan(self.estates[2])
        equal = "1K"
        self.assertEqual(res, equal)

        res = self.obj.estate_to_floorplan(self.estates[5])
        equal = "ワンルーム"
        self.assertEqual(res, equal)

    # 築年数文字列
    def test_str_construction_date_to_str_date(self):
        print('test_str_construction_date_to_str_date')
        str = "1971年4月"
        res = self.obj.str_construction_date_to_str_date(str)
        equal = "1971-04-01"
        self.assertEqual(res, equal)

        # 文字列が入ったパターン とりあえず無視
        str = "平成71年4月"
        res = self.obj.str_construction_date_to_str_date(str)
        equal = ""
        self.assertEqual(res, equal)

        # 文字列なし
        str = ""
        res = self.obj.str_construction_date_to_str_date(str)
        equal = ""
        self.assertEqual(res, equal)

        # 巨大な年数
        str = "9971年4月"
        res = self.obj.str_construction_date_to_str_date(str)
        equal = "9971-04-01"
        self.assertEqual(res, equal)

        # マイナス年数
        str = "-1年4月"
        res = self.obj.str_construction_date_to_str_date(str)
        equal = ""
        self.assertEqual(res, equal)

    # 築年数
    def test_estate_to_construction_date(self):
        print('test_estate_to_construction_date')
        res = self.obj.estate_to_construction_date(self.estates[0])
        equal = "1971-04-01"
        self.assertEqual(res, equal)

    # コメントを取得
    def test_estate_to_comment(self):
        print('test_estate_to_comment')
        # off_set省略
        res = self.obj.estate_to_comment(self.estates[0])
        equal = "■１階部分所在のお部屋です！■南西向き　陽当り良好■敷地内施設充実（スーパー・郵便局・診療所・保育園・銀行ＡＴＭ・その他商店）"
        self.assertEqual(res, equal)

        # off_set=0
        res = self.obj.estate_to_comment(self.estates[1], 0)
        equal = "◆即時ご内見可◆耐震改修工事済みの安心感。ＬＤＫ約１８．５帖の広々としたお部屋と、南バルコニーからの眺望が魅力的な１０階部分。頭金０円・月々３２，４９２円～で購入可能。"
        self.assertEqual(res, equal)

        # コメントなし off_set
        res = self.obj.estate_to_comment(self.estates[11], 1)
        equal = ""
        self.assertEqual(res, equal)

        # コメントなし off_set=0 ＊理論上はないケース
        res = self.obj.estate_to_comment(self.estates[11], 0)
        equal = ""
        self.assertEqual(res, equal)

    # スタッフコメント
    def test_estate_to_comment_staff(self):
        print('test_estate_to_comment_staff')
        # コメントあり
        res = self.obj.estate_to_comment_staff(self.estates[1])
        equal = "「古いマンションは地震が心配」との声をよく耳にしますが、こちらのマンションは耐震補強を行い安全面にも配慮されております。管理組合が管理人を雇用するなど、しっかりと機能している点も魅力です。"
        self.assertEqual(res, equal)

    # off_set
    def test_get_off_set(self):
        print('test_get_off_set')
        # コメントあり
        res = self.obj.get_off_set(self.estates[0])
        equal = 0
        self.assertEqual(res, equal)

        # コメントなし
        res = self.obj.get_off_set(self.estates[11])
        equal = 1
        self.assertEqual(res, equal)

    # estateから必要項目を抽出
    def test_estates_to_hash_estate(self):
        print('test_estates_to_hash_estate')
        # 全項目が取得できているか確認
        res = self.obj.estate_to_hash(self.estates[0])
        res = len(res)
        equal = 11
        self.assertEqual(res, equal)

        res = self.obj.estate_to_hash(self.estates[51])
        res = len(res)
        equal = 11
        self.assertEqual(res, equal)

        # 名称が取れるか
        estate = self.obj.estate_to_hash(self.estates[1])
        res = estate["name"]
        equal = '秀和めじろ台レジデンス'
        self.assertEqual(res, equal)
        # url
        res = estate["url"]
        equal = 'https://suumo.jp/chukomansion/__JJ_JJ010FJ100_arz1030z2bsz1011z2ncz192692323.html'
        self.assertEqual(res, equal)

        # コメントがないケース
        estate = self.obj.estate_to_hash(self.estates[11])
        res = estate['floor_size']
        equal = '29.64'
        self.assertEqual(res, equal)

    # estatesからjson_strを取得して、復元してチェック
    def test_bs_estate_to_hash_estates(self):
        print('test_bs_estate_to_hash_estates')
        estates = self.obj.bs_estates_to_hash_estates(self.estates)
        res = estates[0]["name"]
        equal = "藤の台団地"
        self.assertEqual(res, equal)

        res = estates[99]["name"]
        equal = "ニックハイム向島百花園"
        self.assertEqual(res, equal)

        res = estates[18]["address_str"]
        equal = "東京都町田市玉川学園５"
        self.assertEqual(res, equal)

        res = estates[11]["price_str"]
        equal = '1480万円'
        self.assertEqual(res, equal)

    # save json filename
    def test_get_save_filename(self):
        print('test_get_save_filename')
        # 拡張子json
        title = "hogehoge"
        cnt = 1
        path = DataPath + "tmp"
        filename = self.obj.get_save_filename(title, cnt, path)
        # 日付が入っている pathの後ろ、１１桁
        res = filename[len(path)+1:len(path)+11]
        equal = self.obj.get_today_string()
        self.assertEqual(res, equal)
        # 指定した連番が入っている
        res = filename[-3:]
        equal = "001"
        self.assertEqual(res, equal)
    
        # 拡張子があり
        title = "hogehoge"
        cnt = 99
        path = DataPath + "tmp"
        filename = self.obj.get_save_filename(title, cnt, path)
        # 指定した連番が入っている
        res = filename[-3:]
        equal = "099"
        self.assertEqual(res, equal)

        # タイトルが空
        title = ""
        cnt = 99
        path = DataPath + ""
        filename = self.obj.get_save_filename(title, cnt, path)
        res = filename
        equal = ""
        self.assertEqual(res, equal)

        # カウントが数字以外
        title = "hogehoge"
        cnt = "ghfhgfd"
        path = DataPath + "tmp"
        filename = self.obj.get_save_filename(title, cnt, path)
        res = filename
        equal = ""
        self.assertEqual(res, equal)

    # save file
    def test_save_textfile(self):
        print('test_save_textfile')
        # 通常のファイル名
        filename = DataPath + "output/test"
        extension_name = "json"
        data = "[{'name': 'test', 'address': 'test2'}]"
        res = self.obj.save_textfile(filename, extension_name, data)
        filename_full = filename + "." + extension_name
        self.assertEqual(res, filename_full)
        # filenameのファイルが存在する
        file_existence = os.path.isfile(filename_full)
        self.assertTrue(file_existence)
        # -作成したファイルを削除
        os.remove(filename_full)

        # ファイル名が空
        filename = ""
        data = "[{'name': 'test', 'address': 'test2'}]"
        res = self.obj.save_textfile(filename, extension_name, data)
        equal = ""
        self.assertEqual(res, equal)

        # 保存テキストが空
        filename = "hagehage"
        data = ""
        res = self.obj.save_textfile(filename, extension_name, data)
        equal = ""
        self.assertEqual(res, equal)

        # ファイル名、保存テキストが空
        filename = ""
        data = ""
        res = self.obj.save_textfile(filename, extension_name, data)
        equal = ""
        self.assertEqual(res, equal)

    # request
    def test_get_html_from_url(self):
        print('test_get_html_from_url')
        # 通常
        url = "https://google.com"
        res = self.obj.get_html_from_url(url)
        self.assertIsNotNone(res)

        # urlが空
        url = ""
        equal = ""
        res = self.obj.get_html_from_url(url)
        self.assertEqual(res, equal)

        # urlが無効
        url = "jkfdsjklfsda"
        equal = ""
        res = self.obj.get_html_from_url(url)
        self.assertEqual(res, equal)

        # 存在しないURL
        url = "https://dfjkljsfdkldsjkkjlrgetlrg.com"
        equal = ""
        res = self.obj.get_html_from_url(url)
        self.assertEqual(res, equal)

    def test_main_get_bs_to_savefile(self):
        '通常時の全体的なテスト サイトへrequestを投げない'
        # json形式
        print('test_main_get_bs_to_savefile')
        bs = self.bs
        filename_full = DataPath + "output/test"
        save_file_type = 'json'
        filename = self.obj.main_get_bs_to_savefile(bs, filename_full, save_file_type)
        res = os.path.isfile(filename)
        equal = True
        self.assertEqual(res, equal)

        # CSV形式
        print('test_main_get_bs_to_savefile')
        bs = self.bs
        filename_full = DataPath + "output/test"
        save_file_type = 'csv'
        filename = self.obj.main_get_bs_to_savefile(bs, filename_full, save_file_type)
        res = os.path.isfile(filename_full + "." + save_file_type)
        equal = True
        self.assertEqual(res, equal)

    # main
    def test_main_get_url_to_html_savefile(self):
        '''
        実際にサイトへデータを１ページ分データを取りに行き正常に動作するか確認するテスト。
        '''
        # 普段は重いのでやらない。コメントアウト
        # self.site_url_requre_get()
        pass

    def site_url_requre_get(self):
        '実際サイトへ取りに行くテストの実装'
        print('site_url_requre_get')
        # 初期値
        path = DataPath + "tmp"
        cnt = 1
        # str_date = self.obj.get_today_string()
        # 東京
        title = SiteUrls[0]["name"]
        url = SiteUrls[0]["url"]
        res = self.obj.main_get_url_to_html_savefile(title, url, path, cnt)
        self.assertTrue(res)

        # 神奈川
        title = SiteUrls[1]["name"]
        url = SiteUrls[1]["url"]
        res = self.obj.main_get_url_to_html_savefile(title, url, path, cnt)
        self.assertTrue(res)

        # 埼玉
        title = SiteUrls[2]["name"]
        url = SiteUrls[2]["url"]
        res = self.obj.main_get_url_to_html_savefile(title, url, path, cnt)
        self.assertTrue(res)

        # 千葉
        title = SiteUrls[3]["name"]
        url = SiteUrls[3]["url"]
        res = self.obj.main_get_url_to_html_savefile(title, url, path, cnt)
        self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()
