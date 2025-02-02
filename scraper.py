import requests
import re
import csv
import yaml
import logging
import time
from bs4 import BeautifulSoup

with open("configs/scrapter_configs.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
BASE_URL = config["base_url"]
CSV_FILE = config["csv_file"]
ENCODING = config["encoding"]
RETRY_COUNT = config["retry_count"]

session = requests.Session()


def parse_event(event, writer):
    # ライブタイトル
    event_title = event.find("h3", class_="artistName")
    title = event_title.a.get_text().strip() if event_title else ""

    # 会場
    event_address = event.find('span', class_='address')
    address = event_address.get_text().strip() if event_address else ""

    # 開催時間
    event_date = event.find('p', class_='date')
    date = event_date.contents[0] if event_date else ""

    # 書き込み
    writer.writerow([title, address, date])


def fetch_page(url, retries=RETRY_COUNT):
    for attempt in range(retries):
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions as e:
            logging.warning(f"ページ {url} の読み込みに失敗しました（{e}）。再試行 {attempt + 1}/{retries}")
            time.sleep(1)
    return None


with open(CSV_FILE, mode='w', newline='', encoding=ENCODING, errors='ignore') as file:
    writer = csv.writer(file)
    writer.writerow(['ライブタイトル', '会場', '開催時間'])

    page_number = 1

    while True:
        url = f"{BASE_URL}/page:{page_number}"
        html = fetch_page(url)
        if not html:
            logging.error(f"ページ {page_number} の取得に失敗しました。終了します。")
            break

        soup = BeautifulSoup(html, 'html.parser')
        events = soup.find_all("div", class_=re.compile("whiteBack midBox|whiteBack midBox tour"))

        for event in events:
            parse_event(event, writer)

        next_page = soup.find('span', class_='next').find('a')

        if next_page:
            next_url = next_page.get('href')  # 次ページURLを取得
            if next_url:
                page_number += 1  # 次ページへ進む
                print(f"次のページ: {next_url}")  # 次のページのURLを表示
            else:
                print("次のページが無効です。終了します。")
                break  # 次ページが無効なら終了
        else:
            print("次のページはありません。終了します。")
            break  # 次のページがない場合は終了
print("ライブ情報を 'live_events.csv' に保存しました。")
