# type: ignore
"""
seleniumでtarget 属性をクリックしてタブが遷移をしても１つ目のタブの要素がゼロにならない方法
https://teratail.com/questions/d6bl0tg488h8fd
"""
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


@dataclass(slots=True, frozen=True)
class Crawler:
    url: str
    driver: webdriver.Chrome

    def extract_info(self) -> str:
        "Extract data on the page."
        return self.driver.title

    def main(self) -> list[str]:
        """
        Click the link in the first page,
        then extract data on the new tab.
        Back to the first page and click next link.

        Loop this until the links of first page are exhausted.
        """
        self.driver.get(self.url)
        wait = WebDriverWait(driver, 10)

        # 最初のページのウィンドウ情報を記録しておく
        original_window = self.driver.current_window_handle

        results: list[str] = []

        elements = self.driver.find_elements(
            By.CSS_SELECTOR, "#techblog ul li a"
        )

        for element in elements:
            element.click()

            # 新しいウインドウかタブが開くまで待機
            wait.until(EC.number_of_windows_to_be(2))

            # 新しいウインドウハンドルを見つけるまでループする
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    result = self.extract_info()
                    results.append(result)
                    break

            # 抽出が終わったタブを閉じる
            self.driver.close()

            # サイトへの負荷軽減のため数秒待機
            time.sleep(2)

            # 一番最初のタブに戻る
            self.driver.switch_to.window(original_window)

        return results


if __name__ == "__main__":
    URL: str = "https://gihyo.jp/"
    SERVICE = Service(ChromeDriverManager().install())
    OPTIONS = webdriver.ChromeOptions()

    with webdriver.Chrome(service=SERVICE, options=OPTIONS) as driver:
        driver.implicitly_wait(30)
        crawler = Crawler(URL, driver)
        result: list[str] = crawler.main()
        print(result)
