from flask import Flask, request, jsonify
import sqlite3
import os
from create_db import init_db  # 데이터베이스 초기화 함수 가져오기

app = Flask(__name__)

# 데이터베이스 초기화
if not os.path.exists('site.db'):
    init_db()

def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "딱걸렸어 솔루션 API PROXY"

@app.route('/sites', methods=['GET'])
def get_sites():
    url = request.args.get('url')  # 쿼리 파라미터에서 'url' 가져오기
    conn = get_db_connection()
    
    # 데이터베이스에서 link와 일치하는 항목을 찾습니다.
    data = conn.execute('SELECT link, from_column, reason, frequency FROM sites WHERE link = ?', (url,)).fetchone()
    conn.close()

    # 데이터가 존재할 경우 각 정보를 JSON 응답으로 반환
    if data:
        result = {
            "result": True,
            "link": data["link"],
            "from_column": data["from_column"],
            "reason": data["reason"],
            "frequency": data["frequency"]
        }
    else:
        result = {"result": False}

    return jsonify(result)

@app.route('/reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM reviews').fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

@app.route('/sites', methods=['POST'])
def add_site():
    new_site = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO sites (link)
        VALUES (?, ?, ?, ?)
    ''', (new_site['link'], new_site['from'], new_site['reason'], new_site['frequency']))
    conn.commit()
    conn.close()
    return '', 201

@app.route('/reviews', methods=['POST'])
def add_review():
    new_review = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO reviews (user_id, password, link, review)
        VALUES (?, ?, ?, ?)
    ''', (new_review['user_id'], new_review['password'], new_review['link'], new_review['review']))
    conn.commit()
    conn.close()
    return '', 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=25570, debug=True)