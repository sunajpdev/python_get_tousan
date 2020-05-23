#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
# import sys
import re
from datetime import datetime
import json
import time

import requests
from bs4 import BeautifulSoup
import pandas as pd


class EstateSumo():
    def __init__(self):
        super().__init__()
        self.TodayString = self.get_today_string()

    def main_get_url_to_html_savefile(self, title, base_url, save_path, cnt, save_file_type):
        '取得処理 同名ファイルがすでにある場合は処理をスキップして終了'
        filename_full = self.get_save_filename(title, cnt, save_path)
        check = os.path.isfile(filename_full + "." + save_file_type)
        print(filename_full, check)
        if check:
            res = ""
        else:
            bs = self.main_get_url_to_html(title, base_url, cnt)
            res = self.main_get_bs_to_savefile(bs, filename_full, save_file_type)
        return res

    def main_get_url_to_html(self, title, base_url, cnt):
        'urlからhtmlを取得し、BSを返す'
        url = base_url + "&pn={0}".format(cnt)
        get_html = self.get_html_from_url(url)
        bs = self.html_to_bs(get_html)

        return bs

    def main_get_bs_to_savefile(self, bs, filename_full, save_file_type):
        'BSから必須項目を抽出して、ファイルを保存してファイル名を返す'
        bs_estates = self.html_to_estates(bs)
        estates = self.bs_estates_to_hash_estates(bs_estates)
        if save_file_type == 'json':
            filename = self.save_json(estates, filename_full)
        else:
            filename = self.save_csv(estates, filename_full)
        return filename

    def save_csv(self, estates, filename_full):
        'csv形式でestatesを保存する。 Excelで簡単に開けるようにutf-8BOM形式'
        df = pd.DataFrame(estates)
        df.to_csv(filename_full + "." + "csv", encoding="utf-8_sig", index=False)
        # filename = self.save_textfile(filename_full, "csv", str_estates)

        return filename_full

    def save_json(self, estates, filename_full):
        'json形式でestatesを保存する'
        str_estates = json.dumps(estates, ensure_ascii=False)
        filename = self.save_textfile(filename_full, "json", str_estates)

        return filename

    # BeatifulSoupオブジェクトを返す
    def html_to_bs(self, html):
        return BeautifulSoup(html, "html.parser")

    # 総件数を取得
    def get_total(self, bs):
        res = bs.select_one(".pagination_set-hit")
        total = res.get_text().replace("件", "").replace(",", "") if res else ""
        try:
            total = int(total)
        except ValueError:
            total = 0

        return total

    # 総ページ数を取得
    def get_total_page(self, bs):
        res = bs.select('ol.pagination-parts li')
        count = len(res)
        total_page = bs.select('ol.pagination-parts li')[count - 1].get_text() if count else ""
        try:
            total_page = int(total_page)
        except ValueError:
            total_page = 0
        return total_page

    # urlからリクエストを取得してHTMLを返す
    def url_to_html(self, url):
        html = requests.get(url).text
        return html

    # htmlより物件ごとのbsオブジェクトを取得する
    def html_to_estates(self, bs):
        # select = "#js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body.ofh > div.ui-media > div.ui-media-body.property_unit-info > div > div:nth-child(1) > dl > dd"
        select = "#js-bukkenList  div.property_unit-content"
        estates = bs.select(select)
        return estates

    # 取得する要素
    # 建物名, 所在地, 路線, 最寄駅, 交通手段, 所要時間, 築年数, 階数（個別ページ）,  最低価格, 最高価格
    # 子要素の構造
    # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > 
    # div > div.ui-media-body > div > div:nth-child(3) > table > tbody > tr > td:nth-child(1) > dl > dd

    # bs estateから必要項目を取得する
    def estate_to_hash(self, bs_estate):
        # テーブル数に応じてoff_setを取得
        off_set = self.get_off_set(bs_estate)

        # 路線,駅,バス時間,徒歩時間,車距離は文字列の分解が必要
        # str_routes = self.estate_to_str_routes(bs_estate, off_set)

        hash_estate = {
            'name': self.estate_to_name(bs_estate),
            'url': self.estate_to_url(bs_estate),
            'address_str': self.estate_to_address(bs_estate, off_set),
            'floor_size': self.estate_to_floor_size(bs_estate, off_set),
            'balcony_size': self.estate_to_balcony_size(bs_estate, off_set),
            'floorplan_str': self.estate_to_floorplan(bs_estate, off_set),
            'construction_date': self.estate_to_construction_date(bs_estate, off_set),
            'price_str': self.estate_to_price(bs_estate, off_set),
            'routes_str': self.estate_to_str_routes(bs_estate, off_set),
            # 'route': self.str_routes_to_route(str_routes),
            # 'station': self.str_routes_to_station(str_routes),
            # 'bus_time': self.str_routes_to_traffic_bus(str_routes),
            # 'work_time': self.str_routes_to_traffic_work(str_routes),
            # 'car_distance': self.str_routes_to_traffic_car(str_routes),
            'comment': self.estate_to_comment(bs_estate, off_set),
            'comment_staff': self.estate_to_comment_staff(bs_estate, off_set)
        }
        return hash_estate

    # 建物名を取得
    def estate_to_name(self, bs_estate):
        select = "h2.property_unit-title_wide a"
        res = bs_estate.select(select)[0].get_text()
        return res

    # urlを取得
    def estate_to_url(self, bs_estate):
        select = "h2.property_unit-title_wide a"
        res = "https://suumo.jp" + bs_estate.select(select)[0]['href']
        return res

    # off_set(コメントの有無によるDivのずれ)対応のためのselect分を返す
    def off_set_select(self, position, off_set=0):
        i = position - off_set
        return "div.ui-media-body > div > div.dottable-line:nth-child(" + str(i) + ") >"

    # 所在地を取得
    def estate_to_address(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(11) > div.property_unit-content > div.property_unit-body > div.ui-media > 
        # div.ui-media-body > div > div:nth-child(3) > table > tbody > tr > td:nth-child(1) > dl > dd
        # #js-bukkenList > div:nth-child(12) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(2) > table > tbody > tr > td:nth-child(1) > dl > dd
        position = 3
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(1) > dl > dd"
        res = bs_estate.select_one(select).get_text()
        return res

    # 路線、駅、交通手段などのデータを抽出して、文字列を返す
    def estate_to_str_routes(self, bs_estate, off_set=0):
        position = 4
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(1) > dl > dd"
        return bs_estate.select_one(select).get_text()

    # 販売価格を取得
    def estate_to_price(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(2) > table > tbody > tr > td:nth-child(1) > dl > dd > span
        position = 2
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(1) > dl > dd > span"
        str_price = bs_estate.select_one(select).get_text()
        # res = self.str_price_to_number(str_price)
        return str_price

    # 専有面積の文字列から不要な文字を取り除く
    def clean_str_floor_size(self, str_floor_size):
        pattern = '.*?(\d+\.?\d*|\.\d+)m2'
        result = re.compile(pattern).match(str_floor_size)
        res = result[1] if result else ''
        return res

    # 専有面積を取得
    def estate_to_floor_size(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(2) > table > tbody > tr > td:nth-child(2) > dl > dd
        position = 2
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(2) > dl > dd"
        str_res = bs_estate.select_one(select).get_text()
        res = self.clean_str_floor_size(str_res)
        return res

    # バルコニー面積を取得
    def estate_to_balcony_size(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(3) > table > tbody > tr > td:nth-child(2) > dl > dd
        position = 3
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(2) > dl > dd"
        str_res = bs_estate.select_one(select).get_text()
        res = self.clean_str_floor_size(str_res)
        return res

    # 間取りを取得
    def estate_to_floorplan(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(4) > table > tbody > tr > td:nth-child(2) > dl > dd
        position = 4
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(2) > dl > dd"
        res = bs_estate.select_one(select).get_text()
        return res

    # 築年数を日付文字列で返す
    def str_construction_date_to_str_date(self, str_construction_date):
        pattern = "(\d+)年(\d+)月"
        result = re.compile(pattern).match(str_construction_date)
        if result: 
            d = datetime(int(result[1]), int(result[2]), 1)
            res = d.strftime('%Y-%m-%d')
        else: 
            res = ""
        return res

    # 築年数を取得
    def estate_to_construction_date(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(5) > table > tbody > tr > td:nth-child(2) > dl > dd
        
        # コメントのないケースz
        # #js-bukkenList > div:nth-child(12) > div.property_unit-content > div.property_unit-body > div > 
        # div.ui-media-body > div > div:nth-child(4) > table > tbody > tr > td:nth-child(2) > dl > dd
        position = 5
        select = self.off_set_select(position, off_set) + "table > tbody > tr > td:nth-child(2) > dl > dd"
        str_construction_date = bs_estate.select_one(select).get_text()
        res = self.str_construction_date_to_str_date(str_construction_date)
        return res

    # コメントを取得
    def estate_to_comment(self, bs_estate, off_set=0):
        if off_set == 0:
            # #js-bukkenList > div:nth-child(1) > div.property_unit-content > div.property_unit-body > div > 
            # div.ui-media-body > div > div.dottable-lead > table > tbody > tr > td
            select = "div.ui-media-body > div > div.dottable-lead > table > tbody > tr > td"
            res = bs_estate.select_one(select)
            res = res.get_text() if res else ""
        else:
            res = ""
        return res
    
    # スタッフコメントを取得
    def estate_to_comment_staff(self, bs_estate, off_set=0):
        # #js-bukkenList > div:nth-child(2) > div.property_unit-content > div.property_unit-body > div.dotblock > div > div > p
        select = "#js-bukkenList > div:nth-child(2) > div.property_unit-content > div.property_unit-body > div.dotblock > div > div > p"
        res = bs_estate.select_one(select)
        res = res.get_text() if res else ""
        return res

    # estateのdiv件数をカウントしてoff_setを返す
    def get_off_set(self, bs_estate):
        select = "div.ui-media-body > div > div"
        count = len(bs_estate.select(select))
        off_set = 5 - count
        return off_set

    # bs estates から estateの配列を取得して、配列にして返す
    def bs_estates_to_hash_estates(self, bs_estates):
        res = []
        for bs_estate in bs_estates:
            res.append(self.estate_to_hash(bs_estate))
        return res

    # today string
    def get_today_string(self):
        return datetime.today().strftime('%Y-%m-%d')

    # save filename
    def get_save_filename(self, title, cnt, save_path):
        str_today = self.TodayString
        if title and cnt and str.isdecimal(str(cnt)) and save_path:
            filename = save_path + "/" + "{0}_{1}_{2:03d}".format(str_today, title, cnt)
            return filename
        else:
            return ""

    def save_textfile(self, filename, extension_name, save_text):
        'ファイルを保存し、成功したらフルパスを含むファイル名、失敗したら空文字を返す'
        if filename and extension_name and save_text:
            filename = filename + "." + extension_name
            with open(filename, 'w') as f:
                f.write(save_text)
            return filename
        else:
            return ""

    # get request
    def get_html_from_url(self, url):
        if url:
            try:
                resp = requests.get(url)
                html = resp.text if resp else ""
            except:
                html = ""
            return html
        else:
            return ""
