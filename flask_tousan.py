from flask import Flask, render_template
from src.db import session, engine, func, City, Prefecture, Tousan


app = Flask(__name__)


@app.route('/')
def tousan():
    ''
    last_update = session.query(func.max(Tousan.created)).one()[0].strftime("%Y/%m/%d %H:%M:%S")

    tousans = session.query(Tousan).filter(Tousan.tousan_date >= '2020/1/1').order_by(Tousan.tousan_date.desc()).all()
    return render_template("tousan.html", title='倒産情報', tousans=tousans, last_update=last_update)

@app.route('/prefecture/<prefecture>')
def prefecture(prefecture):
    '都道府県別'
    tousans = session.query(Tousan).filter(
        Tousan.tousan_date >= '2020/1/1', Tousan.prefecture == prefecture).order_by(Tousan.tousan_date.desc()).all()
    
    return render_template("tousan.html", title='倒産情報 都道府県', tousans=tousans)


@app.route('/prefectures')
def prefectures():
    '都道府県全データ'
    cnt = func.count(Tousan.id)
    tousans = session.query(
        cnt.label("cnt"), Tousan.prefecture).filter(Tousan.tousan_date >= '2020/1/1'
        ).group_by(Tousan.prefecture
        ).order_by(cnt.desc()).all()

    return render_template("prefectures.html", title='倒産情報 都道府県集計', prefectures=tousans)


@app.route('/indastries')
def indastries():
    '業種全データ'
    cnt = func.count(Tousan.id)
    tousans = session.query(
        cnt.label("cnt"), Tousan.indastry).filter(Tousan.tousan_date >= '2020/1/1'
        ).group_by(Tousan.indastry
        ).order_by(cnt.desc()).all()

    return render_template("indastries.html", title='倒産情報 業界集計', rows=tousans)


@app.route('/indastry/<indastry>')
def indastry(indastry):
    '業種全データ'
    tousans = session.query(Tousan).filter(Tousan.tousan_date >= '2020/1/1', Tousan.indastry == indastry).order_by(Tousan.tousan_date.desc()).all()
    return render_template("tousan.html", title='倒産情報 業界', tousans=tousans)


if __name__ == "__main__":
    app.run(debug = True, host='192.168.11.4', port=5000)
