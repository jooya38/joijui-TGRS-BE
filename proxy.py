from flask import Flask, request, jsonify
import sqlite3
import os
from create_db import init_db  # 데이터베이스 초기화 함수 가져오기
from urllib.parse import urlparse, urlunparse
from flask_cors import CORS
import time
from OpenSSL import SSL

app = Flask(__name__)
CORS(app)  # 모든 출처에서의 요청을 허용

# 데이터베이스 초기화
if not os.path.exists('site.db'):
    init_db()

def get_db_connection():
    conn = sqlite3.connect('site.db', timeout=10)
    encoding = conn.execute("PRAGMA encoding").fetchone()[0]
    print(f"Database encoding: {encoding}")
    conn.row_factory = sqlite3.Row
    return conn

def execute_with_retry(query, params=(), retries=5, delay=1):
    for attempt in range(retries):
        try:
            conn = get_db_connection()
            conn.execute(query, params)
            conn.commit()
            break
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                print("Database is locked, retrying...")
                time.sleep(delay)  # 잠금이 해제될 때까지 대기
            else:
                raise
        finally:
            conn.close()

def normalize_url(url):
    parsed_url = urlparse(url)
    
    # 스키마 (http, https) 제거
    netloc = parsed_url.netloc.lower()
    
    # www. 제거
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    
    # 경로 소문자 통일 및 끝 슬래시 제거
    path = parsed_url.path.lower().rstrip('/')
    
    # 쿼리 스트링 유지, 프래그먼트 제거
    query = parsed_url.query
    
    # 정규화된 URL 생성 (스키마 제거 후, 불필요한 슬래시 제거)
    normalized_url = f"{netloc}{path}"
    
    # 쿼리가 있는 경우 쿼리 추가
    if query:
        normalized_url += f"?{query}"
    
    return normalized_url

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
            print(normalize_url(row['link']), normalized_url)
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
    execute_with_retry('''
        INSERT INTO sites (link, from_column, reason, frequency)
        VALUES (?, ?, ?, ?)
    ''', (new_site['link'], new_site['from_column'], new_site['reason'], new_site['frequency']))
    return '', 201

@app.route('/reviews', methods=['POST'])
def add_review():
    new_review = request.get_json()
    execute_with_retry('''
        INSERT INTO reviews (user_id, password, link, review)
        VALUES (?, ?, ?, ?)
    ''', (new_review['user_id'], new_review['password'], new_review['link'], new_review['review']))
    return '', 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=25570, debug=True)