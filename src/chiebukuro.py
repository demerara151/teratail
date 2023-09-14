# type: ignore
# CSpell: disable
"""
WebDriverException: Message: no such execution context エラー
https://teratail.com/questions/pptud6144t1b57
"""
import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

options = Options()

# Chrome Betaのバイナリファイルへのパスを設定
chrome_beta_path = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"

# Chrome Beta用のオプションを設定
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chrome_beta_path

# Chrome BetaのWebDriverを起動
chrome_service = ChromeService(
    executable_path="C:/Users/kusph/chromedriver-win64/chromedriver.exe"
)

browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

browser.maximize_window()

# ページ遷移後すぐに要素が見つからない場合に待機する時間の設定
browser.implicitly_wait(10)

url = (
    "https://chiebukuro.yahoo.co.jp/search"
    "?p=%E9%9B%AA%E8%A6%8B%E5%A4%A7%E7%A6%8F"
    "&vaop=a&search=all&flg=3&dflg=4&dfrom_y=2021"
    "&dfrom_m=04&dfrom_d=01&dto_y=2023&dto_m=09&dto_d=11&noct=1"
)

# URLを開く
browser.get(url)

# 各種情報を格納するリストを準備
page_urls: list[str] = []
posted_dates: list[str] = []
texts: list[str] = []

# 質問の総数を取得して表示
total_questions = browser.find_element(
    By.XPATH, "/html/body/div/div/div/div/div[2]/div[1]/div[6]/p"
)
all_split = total_questions.text.split("件")
print(all_split[0])

# 質問の一覧ページを巡回して、URL と 質問日時を収集する
while True:
    headings = browser.find_elements(
        By.CLASS_NAME, "h3.ListSearchResults_listSearchResults__heading__1T_RX"
    )
    for heading in headings:
        page_urls.append(heading.get_attribute("href"))

    dates = browser.find_elements(
        By.CSS_SELECTOR,
        "h3.ListSearchResults_listSearchResults__informationDate__10t00",
    )
    for date in dates:
        posted_dates.append(date.text)

    try:
        next_button = browser.find_element(By.PARTIAL_LINK_TEXT, "次へ")
        next_button.click()
        time.sleep(3)
    except Exception:
        # 次へボタンが見つからない場合、プログラムを終了する
        print("次へボタンが見つかりませんでした。スクレイピングを終了します。")
        browser.quit()
        break


def get_question_text(url: str) -> None:
    "質問ページにアクセスして本文を取得する"

    browser.get(url)

    try:
        question_body = browser.find_element(
            By.CSS_SELECTOR,
            "div.ClapLv2QuestionItem_Chie-QuestionItem__Text__1AI-5",
        )
        texts.append(question_body.text)
        time.sleep(3)

    except Exception as e:
        print("質問の取得に失敗しました:", e)
        print(f"失敗したURL: {url}")
        texts.append("NA")


# リストに格納した URL に順にアクセスして質問文を収集する
for url in page_urls:
    get_question_text(url)

# 収集したデータを一つにまとめる
data = zip(page_urls, posted_dates, texts)

# データを CSV に書き出す
with open("chiebukuro.csv", "w") as f:
    writer = csv.writer(f)
    for row in data:
        writer.writerow(row)

browser.quit()
