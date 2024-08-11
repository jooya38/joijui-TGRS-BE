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
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM sites').fetchall()
    conn.close()
    return jsonify([dict(row) for row in data])

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
        VALUES (?)
    ''', (new_site['link'],))
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
    app.run(host='0.0.0.0', port=8080, debug=True)