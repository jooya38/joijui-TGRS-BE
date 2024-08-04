from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import csv
import time
import re
import sqlite3

# 드라이버 설정 및 웹 페이지 로드
service = Service(r'C:\Users\hwooo\.wdm\drivers\chromedriver\win64\126.0.6478.182\chromedriver-win32\chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get('https://ecc.seoul.go.kr/DR2001/FN2004LS.jsp')
wait = WebDriverWait(driver, 20)

results = []

try:
    page_number = 1
    while True:
        # 현재 페이지의 모든 링크를 찾기
        links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href^="javascript:pageMove("]')))
        
        for index in range(len(links)):
            try:
                # 페이지 로드 후 다시 링크 요소를 찾기
                links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href^="javascript:pageMove("]')))
                link = links[index]
                link.click()
                time.sleep(3)
                
                # 본문 내용을 가져오기
                body = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.view_3'))
                ).text
                
                # 본문에서 영어 단어 추출
                links_in_body = re.findall(r'\b[A-Za-z0-9._%+-]+(?:\.[A-Za-z0-9.-]+)*\.[A-Za-z]{2,}\b', body)
                
                for detail_link in links_in_body:
                    results.append([detail_link])
                    
            except TimeoutException:
                print(f"Timeout while trying to get details from page {index + 1}")
            except NoSuchElementException:
                print(f"Element not found on page {index + 1}")
            except StaleElementReferenceException:
                print(f"Stale element reference on page {index + 1}")
                continue
            
            driver.back()
            time.sleep(3)

        # 다음 페이지로 이동
        page_number += 1
        try:
            next_page = driver.find_element(By.LINK_TEXT, str(page_number))
            next_page.click()
            time.sleep(3)
        except NoSuchElementException:
            break  # 다음 페이지가 없으면 종료

finally:
    with open('site_details.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Link'])
        for result in results:
            writer.writerow(result)

    driver.quit()
    print("Data has been written to CSV.")

    # SQLite 데이터베이스 연결
    conn = sqlite3.connect('site.db')
    c = conn.cursor()

    # 크롤링한 데이터 DB에 삽입
    for result in results:
        c.execute('''
            INSERT INTO sites (link, review, site_id)
            VALUES (?, ?, ?)
        ''', result)  #크롤링 된 리뷰, 크롤링된 ID

    # 변경사항 저장 및 데이터베이스 연결 종료
    conn.commit()
    conn.close()

    print("Data has been inserted into the database.")