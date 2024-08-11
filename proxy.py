from flask import Flask, request, jsonify
import sqlite3
import os
from create_db import init_db  # 데이터베이스 초기화 함수 가져오기
from urllib.parse import urlparse

app = Flask(__name__)

# 데이터베이스 초기화
if not os.path.exists('site.db'):
    init_db()

def get_db_connection():
    conn = sqlite3.connect('site.db')
    encoding = conn.execute("PRAGMA encoding").fetchone()[0]
    print(f"Database encoding: {encoding}")
    conn.row_factory = sqlite3.Row
    return conn

def normalize_url(url):
    parsed_url = urlparse(url)
    
    # Scheme (http, https)를 무시하고 netloc (도메인 이름)과 path만 사용
    domain = parsed_url.netloc.lower().replace('www.', '')
    path = parsed_url.path
    
    return domain + path

@app.route('/')
def home():
    return "딱걸렸어 솔루션 API PROXY"

@app.route('/sites', methods=['GET'])
def get_sites():
    url = request.args.get('url')  # 쿼리 파라미터에서 'url' 가져오기
    normalized_url = normalize_url(url)

    conn = get_db_connection()
    
    data = conn.execute('SELECT * FROM sites').fetchall()
    conn.close()

    # 모든 데이터베이스 URL도 정규화하여 비교
    for row in data:
        if normalize_url(row['link']) == normalized_url:
            result = {
                "result": True,
                "link": row['link'],
                "from": row['from_column'],
                "reason": row['reason'],
                "frequency": row['frequency']
            }
            return jsonify(result)

    return jsonify({"result": False})

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