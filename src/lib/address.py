from src.db import session, engine, City, Prefecture

# 都道府県 変換
def get_prefecture(address):
    address = str(address)
    if "東京都" in address:
        res = "東京都"
    elif "県" in address[:4]:
        res = address[:address.find("県")+1]
    elif "府" in address[:4]:
        res = address[:address.find("府")+1]
    elif "道" in address[:4]:
        res = "北海道"
    else:
        res = ""
    return res


def get_address_to_prefecture_city(address):
    '市町村から都道府県取得'
    # 都道府県がある場合は抽出する
    prefecture = get_prefecture(address)

    # addressから都道府県以下のみ取得する
    search = "%" + str(address).replace(prefecture, '') + "%"
    city = session.query(City.id, City.prefecture_id, Prefecture.name).join(Prefecture).filter(City.name.like(search))
    if prefecture:
        city.filter(Prefecture.name == prefecture)
    res = city.first()
    
    return res