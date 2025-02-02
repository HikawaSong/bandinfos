import requests
import re
import csv
from bs4 import BeautifulSoup

base_url = "https://www.livefans.jp/search/artist/94247"

with open('live_events.csv', mode='w', newline='', encoding='shift_jis',errors='ignore') as file:
    writer = csv.writer(file)
    writer.writerow(['ライブタイトル', '会場', '開催時間']) 

    page_number=1
    
    while True:
        url = f"{base_url}/page:{page_number}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"ページ {page_number} の読み込みに失敗しました。")
            break  # 読み込み失敗した場合は終了
            
        soup = BeautifulSoup(response.text,'html.parser')
        events = soup.find_all("div", class_=re.compile("whiteBack midBox|whiteBack midBox tour"))

        for event in events:
            event_title = event.find("h3", class_="artistName")
            title = event_title.a.get_text().strip() if event_title else ""   # ライブタイトル
            
            # 会場
            event_address = event.find('span', class_='address')
            address = event_address.get_text().strip() if event_address else ""   

            # 開催時間
            event_date = event.find('p', class_='date')
            date = event_date.contents[0] if event_date else "" 

            writer.writerow([title, address, date])

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


