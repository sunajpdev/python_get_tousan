import csv


class LibCsv:
    def open_csv_dict(self, fname):
        '辞書型でCSVを読み込む'
        datas = []
        with open(fname, encoding='utf-8')as f:
            reader = csv.DictReader(f)
            header = next(reader)
            for row in reader:
                datas.append(row)
        return datas

    def save_csv_dict(self, fname, dict_list):
        '辞書型をCSVに保存する'
        header = dict_list[0].keys()
        
        try:
            with open(fname, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                for row in dict_list:
                    writer.writerow(row)
            return True
        except:
            return False