import sqlite3
import csv
import os

def init_db():
    # 데이터베이스 연결
    conn = sqlite3.connect('site.db')
    cur = conn.cursor()

    # 테이블 생성
    # 사기사이트링크(링크(PK))
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            link TEXT PRIMARY KEY
        )
    ''')

    # 리뷰(회원번호, 링크, 리뷰)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            user_id TEXT,
            password TEXT,
            link TEXT,
            review TEXT,
            FOREIGN KEY (link) REFERENCES sites(link)
        )
    ''')

    # site.csv 파일 읽기 및 데이터 삽입
    if os.path.exists('./site.csv'):
        with open('./site.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 헤더 건너뛰기
            for row in reader:
                cur.execute('''
                    INSERT INTO sites (link)
                    VALUES (?)
                ''', (row[0],))
                print(f"Inserted site: {row[0]}")

    # reviews.csv 파일 읽기 및 데이터 삽입
    if os.path.exists('./reviews.csv'):
        with open('./reviews.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # 헤더 건너뛰기
            for row in reader:
                cur.execute('''
                    INSERT INTO reviews (user_id, password, link, review)
                    VALUES (?, ?, ?, ?)
                ''', (row[0], row[1], row[2], row[3]))
                print(f"Inserted review: {row[3]}")

    # 변경사항 저장 및 데이터베이스 연결 종료
    conn.commit()
    conn.close()
    print("Data Initialized")

if __name__ == '__main__':
    init_db()