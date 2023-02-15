# type: ignore
"""
seleniumでtarget 属性をクリックしてタブが遷移をしても１つ目のタブの要素がゼロにならない方法
https://teratail.com/questions/d6bl0tg488h8fd
"""
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def extract_links(driver: webdriver.Chrome) -> list[str]:
    # クリックしたい全ての要素
    elements = driver.find_elements(
        By.XPATH,
        '//*[@id="root"]/div/div/div[5]/div[2]/div[4]/div[5]/'
        "div/div[1]/table/tbody/tr/td[2]/div/div[1]/a",
    )

    # href attribute の URL を保存しておく
    return [element.get_attribute("href") for element in elements]


def extract_info(driver: webdriver.Chrome) -> str:
    # 「1,234」「5,678」のような数字（情報）を引き出す
    numbers = driver.find_element(
        By.XPATH,
        '//*[@id="main"]/div[8]/table[2]/tbody/'
        "tr[1]/td[1]/table/tbody/tr[11]/td[3]",
    )

    # ,をなくす
    return numbers.text.replace(",", "")


def main(driver: webdriver.Chrome, links: list[str]) -> list[str]:
    # 最終結果
    results: list[str] = []

    for link in links:
        driver.get(link)
        result = extract_info(driver)
        results.append(result)
        driver.close()
        time.sleep(2)

    return results


if __name__ == "__main__":
    url: str = ""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()

    with webdriver.Chrome(service=service, options=options) as driver:
        driver.implicitly_wait(30)
        driver.get(url)
        links = extract_links(driver)
        result: list[str] = main(links)
        print(result)
