# type: ignore
"""
seleniumでtarget 属性をクリックしてタブが遷移をしても１つ目のタブの要素がゼロにならない方法
https://teratail.com/questions/d6bl0tg488h8fd
"""
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def extract_info(driver: webdriver.Chrome) -> str:
    # 「1,234」「5,678」のような数字（情報）を引き出す
    numbers = driver.find_element(
        By.XPATH,
        '//*[@id="main"]/div[8]/table[2]/tbody/'
        "tr[1]/td[1]/table/tbody/tr[11]/td[3]",
    )

    # ,をなくす
    return numbers.text.replace(",", "")

    # test
    # return driver.title


def main(url: str, driver: webdriver.Chrome) -> list[str]:
    driver.implicitly_wait(30)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # 最初のページのウィンドウ情報を記録しておく
    original_window = driver.current_window_handle

    # 最終結果
    results: list[str] = []

    # クリックしたい全ての要素
    elements = driver.find_elements(
        By.XPATH,
        '//*[@id="root"]/div/div/div[5]/div[2]/div[4]/div[5]/'
        "div/div[1]/table/tbody/tr/td[2]/div/div[1]/a",
    )

    # test
    # elements = driver.find_elements(By.CSS_SELECTOR, "#techblog ul li a")

    # 全要素の中の各要素に対して処理を実行
    for element in elements:

        # 要素をクリック
        element.click()

        # 新しいウインドウかタブが開くまで待機
        wait.until(EC.number_of_windows_to_be(2))

        # 新しいウインドウハンドルを見つけるまでループする
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                result = extract_info(driver)
                # 結果を保存
                results.append(result)
                break

        # 抽出が終わったタブを閉じる
        driver.close()

        # サイトへの負荷軽減のため数秒待機
        time.sleep(2)

        # 一番最初のタブに戻る
        driver.switch_to.window(original_window)

    return results


if __name__ == "__main__":
    # test
    # URL: str = "https://gihyo.jp/"

    URL: str = ""
    SERVICE = Service(ChromeDriverManager().install())
    OPTIONS = webdriver.ChromeOptions()

    with webdriver.Chrome(service=SERVICE, options=OPTIONS) as driver:
        result: list[str] = main(URL, driver)
        print(result)
